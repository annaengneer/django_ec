from django.shortcuts import render, get_object_or_404,redirect
from .models import Product, Cart, CartItem,Order,OrderProduct,PromoCode
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
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.get(pk=cart_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cartfunc')

def view_cartfunc(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        messages.info(request, "カートが空です")
        return render(request, 'product_cart.html')
    
    cart = Cart.objects.get(id=cart_id)
    cart_items = cart.items.select_related('product')

    if not cart_items.exists():
        messages.info(request, "カートが空です")
        return render(request, 'product_cart.html')
    total = sum(item.product.price * item.quantity for item in cart_items)
    discount = request.session.get('discount', 0)
    total_after_discount = max(total - discount, 0)

    context = {
        'cart_items': cart_items,
        'total': total_after_discount,
        'discount': discount,
        'promo_code': request.session.get('promo_code')
    }

    return render(request,'product_cart.html', context)


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
        print("POSTデータ:", request.POST)

        cart = Cart.objects.get(id=cart_id)
        cart_items = cart.items.select_related('product')
        total =sum(item.product.price * item.quantity for item in cart_items)

        code = request.session.get('promo_code')
        discount = request.session.get('discount', 0)
        promo = None

        if code:
            try:
                promo = PromoCode.objects.get(code=code)
            except PromoCode.DoesNotExist:
                promo = None
        total_discount =max( total - discount, 0)

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
            promo_code=promo,
            total_price=total_discount,
        )
        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )
        
        html_message = """
        <h2>ご注文明細</h2>
        <table border ='1' cellpadding='8'>
        <tr>
        <th>商品名</th>
        <th>数量</th>
        <th>単価</th>
        <th>小計</th>
        </tr>

        """
        for item in cart_items:
            subtotal = item.product.price * item.quantity
            html_message += f"""
            <tr>
              <td>{item.product.name}</td>
              <td>{item.quantity}</td>
              <td>{item.product.price}</td>
              <td>{subtotal}</td> 
            </tr>
            """
        html_message += f"""
        </table>
        <p><strong>割引金額: {discount}円</strong></p>
        <p><strong>合計金額: {total_discount}円</strong></p>
        """
        cart.items.all().delete()
        email = request.POST.get('email')
        if not email:
            messages.error(request,"メールアドレスが入力されていません")
            return redirect('view_cartfunc')
        response = send_email(
            to_email=email,
            subject='ご注文ありがとうございました',
            message='以下に購入明細添付しています。',
            html_message=html_message
        )
        print(f"送信先メールアドレス: {email}")
        print(f"Mailgun response: {response.status_code},{response.text}")
        
        if response.status_code == 200:
            messages.success(request, "ご購入ありがとうございました")
        else:
            messages.warning(request, "ご購入は完了しましたが、メールの送信に失敗しました。")

        request.session.pop('promo_code', None)
        request.session.pop('discount', None)

        return redirect('listfunc')
    
    except Cart.DoesNotExist:
        print("POSTデータ:", request.POST)
        messages.error(request, "カートが見つかりませんでした。")
        return redirect('view_cartfunc')
    
def apply_promo_code(request):
    if request.method == 'POST':
        code = request.POST.get('promo_code')

        if request.session.get('promo_code') == code:
            messages.info(request,"すでにプロモーションコード使用済みです")
            return redirect('view_cartfunc')
        
        try:
            promotion = PromoCode.objects.get(code=code, is_active=True)

            request.session['discount']=promotion.discount_amount
            request.session['promo_code'] = code

            promotion.is_active = False
            promotion.save()

            messages.success(request, f"プロモーションコード{code}が適応されました")
        except PromoCode.DoesNotExist:
            messages.error(request, "無効なプロモコードです")
        return redirect('view_cartfunc')


def send_email(to_email, subject, message,html_message=None):
        data ={
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "text": message,
        }
        if html_message:
            data["html"]= html_message

        response = requests.post(
            f'https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages',
            auth=('api', settings.MAILGUN_API_KEY),
            data=data
        )
        return response


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
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'manage_edit.html', {'form': form})
    
def upload_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'upload product.html',{'form':form})

@basic_auth_required
def manage_order_list(request):
    orders = Order.objects.all().order_by()
    return render(request, 'order_list.html',{'orders':orders})

def manage_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items =order.card_set.select_related('product').all()
    total =sum(item.product.price * item.quantity for item in items)
    return render(request,'order_detail.html', {
        'order': order,
        'items': items,
        'total': total,
    })