from django.contrib import admin
from core.models import Customer, Product, Cart, CartItem, \
    ShippingAddress, Category, Brand


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ('id', 'name')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'brand',
        'category',
        'name',
        'price',
        'description',
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = ('id', 'customer', 'date_ordered')


@admin.register(CartItem)
class CartItem(admin.ModelAdmin):

    list_display = ('id', 'product', 'cart', 'quantity', 'date_added')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer',
        'cart',
        'address',
        'city',
        'state',
        'zipcode',
        'date_added',
    )
