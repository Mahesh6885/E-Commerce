from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Product, ReviewRating
from .forms import ReviewForm
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from orders.models import OrderProduct


def store(request, category_slug=None):
    categories = None
    products = None

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)

    if min_price and min_price.isdigit():
        products = products.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=int(max_price))

    products = products.order_by('id')
    product_count = products.count()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'selected_category': categories,
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    
    in_cart = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(user=request.user, product=single_product).exists()
    else:
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    orderproduct = False
    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True).order_by('-created_at')

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
    }
    return render(request, "store/product_detail.html", context)


def search(request):
    products = []
    product_count = 0
    keyword = request.GET.get('keyword', '').strip()

    if keyword:
        products_list = Product.objects.order_by('-created_date').filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword),
            is_available=True
        )
        product_count = products_list.count()
        paginator = Paginator(products_list, 6)
        page = request.GET.get('page')
        products = paginator.get_page(page)

    context = {
        'products': products,
        'product_count': product_count,
        'keyword': keyword,
    }
    return render(request, 'store/store.html', context)


@login_required(login_url='login')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                messages.error(request, 'Please complete the review fields properly.')
                return redirect(url)
    return redirect(url)