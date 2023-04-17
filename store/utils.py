import datetime
import json

from django.http import JsonResponse

from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()


def cookieCart(request):
    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('CART:', cart)

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:
            if (cart[i]['quantity'] > 0):  # items with negative quantity = lot of freebies
                cartItems += cart[i]['quantity']
                print(f"{i = } | {cart = }")

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    # 'id': product.id,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total,
                }
                items.append(item)

                # if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    """
    Creates (in db) a new order and a new customer for Anonymous User after checkout
    """

    print('User is not logged in')
    print(f"{request.user=}")
    print('COOKIES', request.COOKIES)
    name = data['form']['name']
    print(f"{name=}")
    phone = data['form']['phone']
    print(f"{phone=}")
    email = data['form']['email']
    print(f"{email=}")

    address = data['form']['address']
    print(f"{address=}")
    zipcode = data['form']['zipcode']
    print(f"{zipcode=}")
    city = data['form']['city']
    print(f"{city=}")

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        # if user put email, but did not register, next time they come back and orders something, we will look for...
        # ...their email instead of creating a new account every time
        email=email,
    )
    # we set it outside the create method so that user can put another name with same email

    customer.name = name
    customer.phone_number = phone
    customer.address = address
    customer.zipcode = zipcode
    customer.city = city
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=True,
    )

    for item in items:
        print(f"{item=}")
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=(item['quantity'] if item['quantity'] > 0 else -1 * item['quantity']),
            # negative quantity = freebies
        )
    return customer, order


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])

    if total == order.get_cart_total:
        order.complete = True

    # creating an instance of the shipping address if an address was sent
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            phone_number=data['shipping']['phone'],
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    order.save()
    return JsonResponse('Payment submitted..', safe=False)
