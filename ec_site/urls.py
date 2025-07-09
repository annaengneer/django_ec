from django.urls import path
from . import views
urlpatterns = [
    path('product/list', views.listfunc, name='listfunc'),
    path('product/<int:pk>/', views.detailfunc, name='detailfunc'),
    path('manage/products', views.manage_products, name='manage_products'),
    path('manage/create', views.manage_create, name='manage_create'),
    path('manage/edit/<int:pk>', views.manage_edit, name='manage_edit'),
    path('manage/delete/<int:pk>', views.manage_delete, name='manage_delete' ),
]