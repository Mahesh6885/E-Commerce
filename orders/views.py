import datetime
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product


@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            messages.error(request, 'Please check your information and try again.')
            return redirect('checkout')
    else:
        return redirect('checkout')


@login_required(login_url='login')
def payments(request):
    if request.method == 'POST':
        # Accept either JSON payload or POST form
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            order_number = body.get('orderID')
            transID = body.get('transID')
            payment_method = body.get('payment_method', 'Credit Card')
            status = body.get('status', 'COMPLETED')
        else:
            order_number = request.POST.get('orderID')
            transID = request.POST.get('transID', f'TXN-{uuid.uuid4().hex[:10].upper()}')
            payment_method = request.POST.get('payment_method', 'Cash on Delivery')
            status = 'COMPLETED'

        order = get_object_or_404(Order, user=request.user, is_ordered=False, order_number=order_number)

        # Store payment details
        payment = Payment.objects.create(
            user=request.user,
            payment_id=transID,
            payment_method=payment_method,
            amount_paid=str(order.order_total),
            status=status,
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move CartItems to OrderProduct
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce product stock
            product = Product.objects.get(id=item.product_id)
            product.stock = max(0, product.stock - item.quantity)
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        if request.content_type == 'application/json':
            data = {
                'order_number': order.order_number,
                'transID': payment.payment_id,
            }
            return JsonResponse(data)
        else:
            return redirect(f'/orders/order_complete/?order_number={order.order_number}&payment_id={payment.payment_id}')

    return redirect('home')


@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)

        subtotal = sum(item.product_price * item.quantity for item in ordered_products)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        messages.error(request, "Order details could not be found.")
        return redirect('home')
