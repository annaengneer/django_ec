from django.db import models
from datetime import date
from django.utils import timezone
from cloudinary.models import CloudinaryField
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2 )
    image_url = CloudinaryField('image')

class Cart(models.Model):
   created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
class Order(models.Model):    
    first_name = models.CharField('first_name', max_length=30)
    last_name = models.CharField('last_name', max_length=30)
    user_name = models.CharField('user_name', max_length=30)
    email = models.EmailField('email', max_length=254)
    address = models.CharField('address', max_length=30, blank=True)
    address2 =  models.CharField('address2', max_length=30, blank=True)
    country = models.CharField('country', max_length=30)
    state = models.CharField('state', max_length=30)
    zip = models.CharField('zip', max_length=30)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    # create_at = models.DateField(default=date.today)
    create_at = models.DateTimeField(default=timezone.now)