def get_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.filter(id=cart_id).first()
        if cart:
            return cart
    cart = Cart.objects.create()
    request.session['cart_id'] = cart.id
    return cart