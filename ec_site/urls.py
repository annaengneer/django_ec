from django.urls import path
from . import views
urlpatterns = [
    path('list', views.listfunc, name='listfunc'),
    path('<int:pk>/', views.detailfunc, name='detailfunc'),
]