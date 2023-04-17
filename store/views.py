from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse, Http404
from django.db.models import Q

import json

from store.models import Product, Order, OrderItem, ShippingAddress, Customer, Category, Carousel
from .forms import ContactForm, OrderCreateForm
from .utils import cartData, guestOrder

from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.filter(active=True).filter(is_popular=True)
    categories = Category.objects.filter(is_popular=True)

    carousel = Carousel.objects.all()
    carousel_items_enabled = Carousel.objects.filter(is_enabled=True)
    context = {'items': items,
               'order': order,
               'products': products,
               'categories': categories,
               'cartItems': cartItems,
               'carousel': carousel,
               'carousel_items_enabled': carousel_items_enabled,
               }
    return render(request, 'store/index.html', context)


def shop(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    categories = Category.objects.all()
    products = Product.objects.filter(active=True)
    context = {'items': items, 'order': order, 'products': products, 'cartItems': cartItems, 'categories': categories}
    return render(request, 'store/shop.html', context)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product.html'
    context_object_name = 'product'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        data = cartData(self.request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']
        product = context['product']
        context = {'items': items, 'order': order, 'cartItems': cartItems, 'product': product}
        return context


class CategoryView(ListView):
    model = Product
    template_name = 'store/shop.html'
    context_object_name = 'products'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(id=self.kwargs['category_id'])
        return context

    def get_queryset(self):
        return Product.objects.filter(category=self.kwargs['category_id'])


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    form = OrderCreateForm()
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(user=request.user.id)
        print(f"{customer=}")

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid() and cartItems > 0:
            name = form.cleaned_data.get('name')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            city = form.cleaned_data.get('city')
            shipping_address = ShippingAddress(
                order=order,
                customer=request.user.customer,
                name=name,
                phone_number=phone_number,
                address=address,
                zipcode=zipcode,
                city=city,
            )

            # when user is logged in, find them in database and update their info
            customer.name = name
            customer.phone_number = phone_number
            # if address != "":
            customer.address = address
            if zipcode != "":
                customer.zipcode = zipcode
            # if city != "":
            customer.city = city
            customer.save()

            order.customer.name = name
            order.customer.email = request.user.customer.email
            shipping_address.save()
            order.shipping_address = shipping_address
            order.complete = True

            order.save()
            return redirect('success')
        # messages.warning(request, 'Оформление не удалось. Возможно, ваша корзина пуста.')
        return redirect('checkout')

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'green': 'GREEN', 'form': form}
    return render(request, 'store/checkout.html', context)


def confirmation(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/confirmation.html', context)


def contact(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # contact form view
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            return redirect('email_sent')

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'form': form}
    return render(request, 'store/contact.html', context)


class SuccessView(UserPassesTestMixin, TemplateView):
    template_name = 'store/success.html'

    def test_func(self):
        if previous_page := self.request.META.get('HTTP_REFERER'):
            print(f"{previous_page=}")
            return True
        else:
            print(f"{previous_page=}")
            return False

    def handle_no_permission(self):
        raise Http404


class EmailSentView(UserPassesTestMixin, TemplateView):
    template_name = 'store/email_sent.html'

    def test_func(self):
        if previous_page := self.request.META.get('HTTP_REFERER'):
            print(f"{previous_page=}")
            return True
        else:
            print(f"{previous_page=}")
            return False

    def handle_no_permission(self):
        raise Http404


def about(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/about.html', context)


class SearchResultsListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
            # for SQLite
            | Q(name__icontains=query.capitalize()) | Q(description__icontains=query.capitalize())
        )


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action', action)
    print('Product', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Controls item quantities when user is logged in
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'delete':
        orderItem.quantity = 0

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

# @csrf_exempt
def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = data['form']['total']  # see checkout.html userFormData -> total
    # check if the total that was passed in above is the same as cart_total (prevents unwanted user manipulation of the Total)
    # without this line: total='599,00' | order.get_cart_total=Decimal('599.00')
    total = total.replace(",", ".")

    if total == str(order.get_cart_total):
        order.complete = True
    order.save()

    # creating an instance of the shipping address if an address was sent
    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            phone_number=data['shipping']['phone'],
            address=data['shipping']['address'],
            zipcode=data['shipping']['zipcode'],
            city=data['shipping']['city'],
        )
        print(f"{data=}")

    return JsonResponse('Payment complete', safe=False)
