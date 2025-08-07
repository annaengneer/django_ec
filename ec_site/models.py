from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import date
from django.utils import timezone
from cloudinary.models import CloudinaryField
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    image_url = CloudinaryField('image')
    description = models.TextField(blank=True)

class Cart(models.Model):
   created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
class PromoCode(models.Model):
    code= models.CharField(
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]{7}$',
                message='プロモションコードは7桁の英数字'
            )
        ]
    )
    discount_amount = models.IntegerField(
        validators=[
            MinValueValidator(100),
            MaxValueValidator(1000)
        ]
    )
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.code} - ¥{self.discount_amount}割引"

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
    create_at = models.DateTimeField(default=timezone.now)