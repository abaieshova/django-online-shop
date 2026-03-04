from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
from .forms import UserRegistrationForm

def product_list(request):
    products = Product.objects.all()
    # Ensure cart exists in session
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return render(request, 'shop/product_list.html', {'products': products})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('shop:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('shop:product_list')

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {'quantity': 1, 'price': str(product.price), 'name': product.name}
    request.session['cart'] = cart
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for pid, item in cart.items():
        subtotal = float(item['price']) * item['quantity']
        total_price += subtotal
        cart_items.append({
            'product_id': pid,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': item['quantity'],
            'subtotal': subtotal
        })
    return render(request, 'shop/cart_detail.html', {'cart': cart_items, 'total': total_price})

@login_required(login_url='shop:login')
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        total_amount = 0
        for pid, item in cart.items():
            product = Product.objects.get(id=pid)
            price = float(item['price'])
            quantity = item['quantity']
            total_amount += (price * quantity)
            OrderItem.objects.create(
                order=order, product=product, price=price, quantity=quantity
            )
            # update stock
            product.stock -= quantity
            product.save()
        
        order.total_amount = total_amount
        order.save()
        request.session['cart'] = {}  # clear cart
        return redirect('shop:orders')
        
    return render(request, 'shop/checkout.html', {'cart': cart})

@login_required(login_url='shop:login')
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': user_orders})
