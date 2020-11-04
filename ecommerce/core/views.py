from itertools import chain

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import (CreateView, DetailView, ListView, UpdateView,
                                  View)

from core.decorators import unauthenticated_user
from core.forms import CreateUserForm, ProfileForm
from core.models import Cart, CartItem, Product
from core.tokens import account_activation_token
from core.utils import (account_confirmation_mail, cartData,
                        product_confirmation_mail)


User = get_user_model()


@method_decorator(login_required, name='dispatch')
class SearchView(ListView):

    '''A class that recivied the search query and gives the 
        results based on that query'''

    template_name = 'search_result.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        data = cartData(self.request)
        context['brands'] = data['brands']
        context['cart'] = data['cart']
        context['categories'] = data['categories']
        context['cart_items'] = data['cart_items']
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)

        if query is not None:
            product_results = Product.objects.search(query)

            queryset_chain = chain(product_results)
            query_set = sorted(queryset_chain, key=lambda instance:
                               instance.pk, reverse=True)
            self.count = len(query_set)
            return query_set
        return Product.objects.none()


@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):

    ''' A default home view when user is enter after login '''

    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = cartData(self.request)
        context['brands'] = data['brands']
        context['cart'] = data['cart']
        context['categories'] = data['categories']
        context['cart_items'] = data['cart_items']
        return context


@method_decorator(login_required, name='dispatch')
class ItemDetailView(DetailView):

    ''' It provide the details of the singal item which user is clicked '''

    model = Product
    template_name = 'single_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = cartData(self.request)

        item = Product.objects.get(id=self.kwargs.get('pk'))
        related_item = Product.objects.filter(brand=item.brand.id)[:3]

        context['brands'] = data['brands']
        context['cart'] = data['cart']
        context['categories'] = data['categories']
        context['related_item'] = [i for i in related_item if i.id !=
                                   self.kwargs.get('pk')]

        return context


@method_decorator(login_required, name='dispatch')
class CartView(ListView):

    ''' Provide the cart details for particular user '''

    template_name = 'cart.html'
    model = Cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = cartData(self.request)
        context['cart'] = data['cart']
        context['items'] = data['items']
        context['cart_items'] = data['cart_items']

        return context


@method_decorator(login_required, name='dispatch')
class FilterCategoryView(ListView):

    ''' It will return the products list based on category 
        and brand selection '''

    model = Product
    template_name = 'search_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs.get('choice') == 'category':
            items = Product.objects.filter(category=self.kwargs.get('pk'
                                                                    ))
        else:
            items = Product.objects.filter(brand=self.kwargs.get('pk'))

        data = cartData(self.request)
        context['brands'] = data['brands']
        context['cart'] = data['cart']
        context['categories'] = data['categories']
        context['cart_items'] = data['cart_items']
        context['object_list'] = items

        return context


@method_decorator(login_required, name='dispatch')
class ProfileView(UpdateView):

    ''' User Profile '''

    model = User
    form_class = ProfileForm
    success_url = reverse_lazy('home')
    template_name = 'registration/profile.html'


@login_required
def update_user_cart(request):
    ''' Update the user cart deails '''

    if request.method == 'POST':
        product_id = request.POST.get('productId')
        action = request.POST.get('action')
        customer = request.user.customer
        product = Product.objects.get(id=product_id)
        (cart, created) = Cart.objects.get_or_create(customer=customer)
        (cart_item, created) = \
            CartItem.objects.get_or_create(cart=cart, product=product)

        if action == 'add':
            cart_item.quantity = cart_item.quantity + 1
        else:
            cart_item.quantity = cart_item.quantity - 1

        cart_item.save()

        if cart_item.quantity <= 0:
            cart_item.delete()

    return JsonResponse('Item was updated', safe=False)


@login_required
def remove_user_cart(request):
    ''' Remove the user cart deails '''

    if request.method == 'POST':
        product_id = request.POST.get('productId')
        customer = request.user.customer
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get(customer=customer)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()

    return JsonResponse('Item was updated', safe=False)


@login_required
def checkout(request):
    ''' A Checkout page '''
    product_confirmation_mail(request)
    return redirect('home')


@method_decorator(unauthenticated_user, name='dispatch')
class SignupView(CreateView):

    ''' Sign up with email confirmation '''

    form_class = CreateUserForm
    template_name = 'registration/signup.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            account_confirmation_mail(request, user)
            messages.success(
                request, ('Please Confirm your email to complete registration.'))

            return redirect('login')
        return render(request, self.template_name, {'form': form})


class ActivateAccount(View):
    ''' Account activation from email token '''

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('home')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('home')
