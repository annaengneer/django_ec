from django.shortcuts import render, get_object_or_404
from .models import Product

# Create your views here.

def listfunc(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products':products})

def detailfunc(request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request,'product_detail.html', {'product': product})