# Generated by Django 5.2.1 on 2025-07-02 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ec_site', '0003_alter_product_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.ImageField(upload_to='product_images/'),
        ),
    ]
