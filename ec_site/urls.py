from django.urls import path
from . import views
from ec_site import views
urlpatterns = [
    path('product/list', views.listfunc, name='listfunc'),
    path('product/<int:pk>', views.detailfunc, name='detailfunc'),
    path('product/cart/',views.view_cartfunc,name='view_cartfunc'),
    path('product/add/<int:pk>', views.add_cartfunc,name='add_cartfunc'),
    path('product/cart/promo', views.apply_promo_code, name='apply_promo_code'),
    path('product/delete/<int:pk>', views.delete_cartfunc, name='delete_cartfunc'),
    path('product/purchase', views.cart_purchasefunc, name='cart_purchasefunc'),
    path('reset/', views.reset_cart, name="reset_cart"),
    path('manage/products', views.manage_products, name='manage_products'),
    path('manage/create', views.manage_create, name='manage_create'),
    path('manage/edit/<int:pk>', views.manage_edit, name='manage_edit'),
    path('manage/delete/<int:pk>', views.manage_delete, name='manage_delete' ),
    path('manage/orders', views.manage_order_list, name='manage_order_list'),
    path('manage/orders/<int:pk>', views.manage_order_detail, name='manage_order_detail'),
]