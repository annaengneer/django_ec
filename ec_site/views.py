from django.shortcuts import render, get_object_or_404,redirect
from .models import Product
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
    cart = request.session.get('cart', {})
    cart[str(product.id)] = cart.get(str(product.id), 0) + quantity
    request.session['cart'] = cart

    return redirect('view_cartfunc')

def view_cartfunc(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    item_count = 0
    print("DEBUG: item_count =", item_count)

    for product_id, quantity in cart.items():
        product= Product.objects.get(pk=int(product_id))
        subtotal = product.price * quantity
        total += subtotal
        item_count += quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal':subtotal,
        })
    return render(request,'product_cart.html',{
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
    })

@require_POST
def delete_cartfunc(request, pk):
    cart = request.session.get('cart',{})
    product_id = str(pk)
    quantity = int(request.POST.get('quantity', 1))
    if product_id in cart:
        cart[product_id] -= quantity
        if cart[product_id] == 0:
            del cart[product_id]
        request.session['cart'] = cart
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
