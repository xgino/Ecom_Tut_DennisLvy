import json
from .models import Customer, Product, Order, OrderItem, ShippingAddress


def cookieCart(request):

    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
    cartItems = order['get_cart_item']

    for i in cart:
        # Use Try Block to prevent items in cart that mamy have been removed from causing errors
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_item'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}



def cartData(request):
    if request.user.is_authenticated:
        custumer = request.user.customer
        order, created = Order.objects.get_or_create(customer=custumer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_item
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}



def guestOrder(request, data):
    print("Not Logged in as User")
    print('COOKIES:', request.COOKIES)

    # Get Data of form
    name = data['form']['name']
    email = data['form']['email']

    # Get cookie product items
    cookieData = cookieCart(request)
    items = cookieData['items']

    # Remember user if they not made account yet. They can see there perviouse orders
    customer, created = Customer.objects.get_or_create(
        email = email,
    )

    # use custumer name outside create function, so they can change there name
    customer.name = name
    customer.save()

    # Create an Order
    order = Order.objects.create(
        customer = customer,
        complete = False, # False because they havnt payed yet, its from Models
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id']) # This comming from utils.py cookieData()
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity'], # This comming from utils.py cookieData()
        )

    return customer, order