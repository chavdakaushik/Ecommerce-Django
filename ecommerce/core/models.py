from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Customer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                null=True, blank=True)
    email = models.EmailField(max_length=200, null=True)


class Brand(models.Model):

    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.name)


class Category(models.Model):

    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.name)


class ProductManager(models.Manager):

    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = Q(name__icontains=query) \
                | Q(brand__name__icontains=query) \
                | Q(category__name__icontains=query)
            qs = qs.filter(or_lookup).distinct()
        return qs


class Product(models.Model):

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,
                              null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount = models.IntegerField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(max_length=500, null=True,
                                   blank=True)
    objects = ProductManager()

    def __str__(self):
        return self.name

    @property
    def get_discount_price(self):
        a = self.discount / 100
        res = a * float(self.price)
        return float(self.price) - res

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Cart(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        cart_items = self.cartitem_set.all()
        total = sum([cart.get_total for cart in cart_items])
        return total

    @property
    def get_cart_items(self):
        cart_items = self.cartitem_set.all()
        total = sum([cart.quantity for cart in cart_items])
        return total


class CartItem(models.Model):

    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                null=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL,
                                 null=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
