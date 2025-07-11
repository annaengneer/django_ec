from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2 )
    image_url = CloudinaryField('image')