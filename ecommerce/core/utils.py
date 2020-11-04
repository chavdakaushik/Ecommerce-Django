import json

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.models import Brand, Cart, Category, Product
from core.tasks import confirmation_email_task
from core.tokens import account_activation_token


def account_confirmation_mail(request, user):
    ''' Account confirmation mail '''
    current_site = get_current_site(request)
    subject = 'Active Your Account'
    context = {'user': user, 'domain': current_site.domain, 'uid': urlsafe_base64_encode(
        force_bytes(user.pk)), 'token': account_activation_token.make_token(user)}
    message = render_to_string(
        'email/account_activation_email.html', context)
    # user.email_user(subject, message)
    user_id = user.pk
    return confirmation_email_task.delay(user_id, subject, message)


def product_confirmation_mail(request):
    ''' Send the email to user when click on checkout '''
    data = cartData(request)
    context = {}
    context['user'] = request.user
    context['cart'] = data['cart']
    context['items'] = data['items']
    context['cart_items'] = data['cart_items']

    subject = 'Thank you for buying products'

    message = render_to_string(
        'email/product_confirmation_email.html', context)
    user_id = request.user.pk
    return confirmation_email_task.delay(user_id, subject, message)


def cookieCart(request):
    ''' Store the anonymous user data to the cookie '''
    try:
        cookie_data = request.COOKIES['cart']
        carts = json.loads(cookie_data)
    except Exception as e:
        carts = {}

    items = []
    cart = {'get_cart_items': 0, 'get_cart_total': 0}
    cart_items = cart['get_cart_items']

    for i in carts:
        try:
            cart_items += carts[i]['quantity']
            product = Product.objects.get(id=i)
            total = product.price * carts[i]['quantity']
            cart['get_cart_total'] += total
            cart['get_cart_items'] += carts[i]['quantity']
            item = {'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.imageURL,
            }, 'quantity': carts[i]['quantity'], 'get_total': total}
            items.append(item)
        except Exception as e:
            pass
    return {'cart_items': cart_items, 'cart': cart, 'items': items}


def cartData(request):
    ''' Cart and related information '''
    if request.user.is_authenticated:
        customer = request.user.customer
        (cart, created) = Cart.objects.get_or_create(customer=customer)
        items = cart.cartitem_set.all()
        cart_items = cart.get_cart_items
    else:
        cookieData = cookieCart(request)
        cart_items = cookieData['cart_items']
        cart = cookieData['cart']
        items = cookieData['items']

    brands = Brand.objects.all()
    categories = Category.objects.all()

    return {
        'brands': brands,
        'categories': categories,
        'items': items,
        'cart_items': cart_items,
        'cart': cart,
    }
