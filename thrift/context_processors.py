def cart_item_count(request):
    if not request.user.is_authenticated:
        return {'cart_item_count' : 0}
    
    try:
        cart = request.user.cart
        count = cart.cart_items.count()
    except:
        count = 0

    return {'cart_item_count': count}