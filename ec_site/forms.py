from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Product

class CustomImage(ClearableFileInput):
    initial_text = "現在の画像"
    input_text = "画像変更"

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image_url', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'price':forms.NumberInput(attrs={
                'class': 'form-control',
            }),

            'image_url': CustomImage(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'height: 150px',
            }),
        }