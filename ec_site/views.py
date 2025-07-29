from django.shortcuts import render, get_object_or_404,redirect
from .models import Product, Cart, CartItem,Order,Card
from .forms import ProductForm
from utils.basic_auth import basic_auth_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import ProductForm
from utils.cart import get_cart
from django.contrib import messages
from django.conf import settings
import requests
from django.http import HttpResponse


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
    cart_items = cart.items.select_related('product')

    total = sum(item.product.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    print("DEBUG: item_count =", item_count)

    return render(request,'product_cart.html',{
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
    })



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

@require_POST
def cart_purchasefunc(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        messages.error(request,"カートが空です。")
        return redirect('view_cartfunc')
    
    try:
        cart = Cart.objects.get(id=cart_id)
        cart_items = cart.items.select_related('product')
        total =sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            user_name=request.POST.get('username', ''),
            email=request.POST.get('email',''),
            address=request.POST.get('address',''),
            address2=request.POST.get('address2', ''),
            country=request.POST.get('country', ''),
            state=request.POST.get('state', ''),
            zip=request.POST.get('zip', ''),
        )
        
        for item in cart_items:
            Card.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        cart.items.all().delete()

        messages.success(request, "ご購入ありがとうございます")
        print("メール送信を開始します")
        send_email(
            to_email=request.POST.get('email'),
            subject='ご注文ありがとうございました',
            message='ご注文受け付けました。近日中に発送します。'
        )
        print("メール送信を呼び出しました")
        return redirect('listfunc')
    
    except Cart.DoesNotExist:
        print("POSTデータ:", request.POST)
        messages.error(request, "カートが見つかりませんでした。")
        return redirect('view_cartfunc')

def send_email(to_email, subject, message):
    return requests.post(
        f'https://api.mailgun.net/v3/{setting.MAILGUN_DOMAIN}/messages',
        auth=('api', settings.MAILGUN_API_KEY),
        data={
            'from':settings.DEFAULT_FROM_EMAIL,
            'to':[to_email],
            'subject': subject,
            "text": message
        }
    )
def test_mail(request):
    send_email(
        to_email='kokoan438@gmail.com',
        subject='テスト送信',
        message='これはMailgunからのテスト送信です'
    )
    return HttpResponse('送信しました')

def order_success(request):
    return render(request, 'order_success.html')

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
