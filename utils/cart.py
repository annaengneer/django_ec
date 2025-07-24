from ec_site.models import Cart
def get_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart, created = Cart.objects.get_or_create(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    return cart