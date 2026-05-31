from django.contrib import admin
from django.urls import path, include
from thrift import views

urlpatterns = [
    path('', views.home, name="home"),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('account', views.account, name='account'),
    path('account/previous-orders/', views.previous_orders, name='previous_orders'),
    path('account/edit-user-information/', views.edit_user_information, name='edit_user_information'),
    path('account/add-item/analyze', views.analyze_item_draft, name='analyze_item_draft'),
    path('account/add-item/', views.add_item, name='add_item'),
    path('account/previous-listed-items/', views.previous_listed_items, name='previous_listed_items'),
    path('about', views.about, name='about'),
]
