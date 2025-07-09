from django.shortcuts import render, get_object_or_404,redirect
from .models import Product
from .forms import ProductForm
from utils.basic_auth import basic_auth_required
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def listfunc(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products':products})

def detailfunc(request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request,'product_detail.html', {'product': product})

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

