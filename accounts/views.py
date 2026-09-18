from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from carts.models import Cart, CartItem
from carts.views import _cart_id


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            # Ensure unique username
            base_username = username
            counter = 1
            while Account.objects.filter(user_name=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                user_name=username,
                password=password,
            )
            user.phone_number = phone_number
            user.is_active = True
            user.save()

            # Create UserProfile
            UserProfile.objects.get_or_create(user=user)

            messages.success(request, 'Registration successful! You can now sign in to your account.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Sync guest session cart to user account
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)
                if cart_items.exists():
                    for item in cart_items:
                        # Check if user already has identical item with same variations
                        existing_user_items = CartItem.objects.filter(user=user, product=item.product)
                        item_variations = list(item.variations.all())
                        matched = False
                        for u_item in existing_user_items:
                            if list(u_item.variations.all()) == item_variations:
                                u_item.quantity += item.quantity
                                u_item.save()
                                item.delete()
                                matched = True
                                break
                        if not matched:
                            item.user = user
                            item.cart = None
                            item.save()
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.user_name}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    from orders.models import Order
    orders = Order.objects.order_by('-created_at').filter(user=request.user, is_ordered=True)
    orders_count = orders.count()
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'orders': orders[:5],
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def my_orders(request):
    from orders.models import Order
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'orders': orders,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password does not match.')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('change_password')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('change_password')

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password updated successfully! Please login with your new password.')
        return redirect('login')

    context = {
        'userprofile': userprofile,
    }
    return render(request, 'accounts/change_password.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    from orders.models import Order, OrderProduct
    order = get_object_or_404(Order, order_number=order_id, user=request.user, is_ordered=True)
    order_detail = OrderProduct.objects.filter(order=order)
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    subtotal = sum(item.product_price * item.quantity for item in order_detail)

    context = {
        'order': order,
        'order_detail': order_detail,
        'subtotal': subtotal,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/order_detail.html', context)
