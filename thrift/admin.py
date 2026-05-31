from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, Product, ProductImage, Cart, CartItem

# Register your models here.
@admin.register(User)
class CustomserAdmin(UserAdmin):
    model = User
    #UserAdmin ka main benefit passwrod hashinbg and all handle krleta hai

    list_display = ('email', 'first_name', 'last_name',  'phone_number', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name',  'phone_number')
    ordering = ('email',)

    # when user already created
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # when new user is craeted ythis form is loaded
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'custom_label', 'full_name', 'city', 'state', 'pincode', 'is_default')
    list_filter = ('address_type', 'city', 'state', 'is_default')
    search_fields = ('user__email', 'full_name', 'phone_number', 'city', 'pincode')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'condition', 'price', 'created_at')
    list_filter = ('category', 'condition', 'created_at')
    search_fields = ('title', 'description', 'seller__email')
    ordering = ('-created_at',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'uploaded_at')
    search_fields = ('product__title',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'added_at')
    search_fields = ('cart__user__email', 'product__title')
