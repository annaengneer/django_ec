from django.shortcuts import render, get_object_or_404,redirect
from .models import Product, Cart, CartItem
from .forms import ProductForm
from utils.basic_auth import basic_auth_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import ProductForm


# Create your views here.

def listfunc(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def detailfunc(request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request,'product_detail.html', {'product': product})

def cartfunc(request):
    product = Product.objects.all()
    return render(request, 'product_cart.html', {'products': product})

def reset_cart(request):
    request.session.flush()
    return redirect('listfunc')

@require_POST
def add_cartfunc(request,pk):
    product = get_object_or_404(Product, pk=pk)
    quantity= int(request.POST.get('quantity', 1))
    cart = get_cart(request)
    
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity += quantity
    item.save()

    return redirect('view_cartfunc')

def view_cartfunc(request):
    cart = get_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)

    total = sum(item.product.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    print("DEBUG: item_count =", item_count)

    return render(request,'product_cart.html',{
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
    })
def get_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.filter(id=cart_id).first()
        if cart:
            return cart
    cart = Cart.objects.create()
    request.session['cart_id']= cart.id
    return cart

def save_cart_id(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    return cart

@require_POST
def delete_cartfunc(request, pk):
    cart = get_cart(request)
    try:
        item = CartItem.objects.get(cart=cart, product__pk=pk)
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
    except CartItem.DoesNotExist:
        pass
    return redirect('view_cartfunc')


@basic_auth_required
def manage_products(request):
    products = Product.objects.all()
    return render(request, 'manage_products.html', {'products': products})

def manage_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm()
    return render(request, 'manage_create.html', {'form': form})

def manage_edit(request,pk):
    products = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=products)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=products)
    return render(request, 'manage_edit.html', {'form': form, 'product': products})

def manage_delete(request,pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        return redirect('manage_products')
    
def upload_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'upload product.html',{'form':form})
