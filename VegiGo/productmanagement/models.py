from django.db import models

# Create your models here.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images')
    description = models.TextField()

    def __str__(self):
        return self.name
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField()
    primary_image = models.ImageField(upload_to='product_images/')


class SecondaryImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/secondary/')

