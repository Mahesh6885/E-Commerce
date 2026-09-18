from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Product, Variation
from .models import Cart, CartItem
from accounts.models import UserProfile


def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    if current_user.is_authenticated:
        # Authenticated user flow
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            existing_variation_list = []
            id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id_list.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)
                if item.quantity < product.stock:
                    item.quantity += 1
                    item.save()
                    messages.success(request, f"Updated quantity for {product.product_name}.")
                else:
                    messages.warning(request, f"Cannot add more. Only {product.stock} items available in stock.")
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                messages.success(request, f"Added {product.product_name} to your cart.")
        else:
            item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
            messages.success(request, f"Added {product.product_name} to your cart.")
        return redirect('cart')

    else:
        # Guest user flow
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            existing_variation_list = []
            id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id_list.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)
                if item.quantity < product.stock:
                    item.quantity += 1
                    item.save()
                    messages.success(request, f"Updated quantity for {product.product_name}.")
                else:
                    messages.warning(request, f"Cannot add more. Only {product.stock} items available in stock.")
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                messages.success(request, f"Added {product.product_name} to your cart.")
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
            messages.success(request, f"Added {product.product_name} to your cart.")
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
        messages.info(request, f"Removed {product.product_name} from your cart.")
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        cart_items = []

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        if not cart_items.exists():
            messages.warning(request, "Your cart is empty. Please add some products to checkout.")
            return redirect('store')

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        return redirect('store')

    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'userprofile': userprofile,
    }
    return render(request, 'store/checkout.html', context)
