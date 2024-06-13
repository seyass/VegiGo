from django.db import models
from authentication.models import vgUser
from django.core.validators import MinValueValidator, MaxValueValidator
from vgadmin import models as place
from django.utils import timezone
from decimal import Decimal


class Location(models.Model):
    name = models.CharField(max_length=100)

class Category(models.Model):
    name = models.CharField(unique = True,max_length=100)
    image = models.ImageField(upload_to='category_images')
    description = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    WEIGHT_CHOICE = {
        ('kg','Kg'),
        ('l','L'),
        ('g','G'),
    }


    name = models.CharField(unique = True,max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    primary_image = models.ImageField(upload_to='product_images/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    unit_type = models.CharField(max_length=10,choices=WEIGHT_CHOICE,default='kg')
    special_discount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    max_discount = models.DecimalField(max_digits=4,decimal_places=2,default=0)
    

    def __str__(self):
        return self.name


    def calculate_discount(self):
        """
        Calculate the discount percentage based on the difference between price and selling price.
        """
        if self.price > 0:
            self.discount = ((self.price - self.selling_price) / self.price) * 100
        else:
            self.discount = 0

        # Round the discount to two decimal places
        self.discount = round(self.discount, 2)

    def save(self, *args, **kwargs):
        """
        Override the save method to calculate discount before saving the product.
        """
        if not self.pk:  # If the product is being created
            # Calculate special_discount only if it's not provided
            if self.selling_price is not None and self.special_discount is None:
                self.special_discount = self.selling_price
        # Calculate the discount before saving
        self.calculate_discount()
        super().save(*args, **kwargs)

class SecondaryImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/secondary/')

class Review(models.Model):
    user = models.ForeignKey(vgUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


class ProductLocations(models.Model):

    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    location = models.ForeignKey(place.Branches,on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('product','location')

    def __str__(self):
        return f"{self.product.name} - {self.location.name} : {self.quantity}"
    

class CategoryOffer(models.Model):

    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=4,decimal_places=2)
    description = models.TextField(blank=True,null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    STATUS_CHOICES = [
        ('expired', 'Expired'),
        ('active', 'Active'),
        ('upcoming', 'Upcoming')
    ]

    # Add the status field with choices and a default value
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    def __str__(self):
        return f"{self.category} - {self.discount}% off"

    # Create a function to update the status field
    def update_status(self):
        current_date = timezone.now().date()
        if self.end_date < current_date:
            self.status = 'expired'
        elif self.start_date <= current_date <= self.end_date:
            self.status = 'active'
        elif self.start_date > current_date and self.end_date > current_date:
            self.status = 'upcoming'
    
    # Override the save method to automatically update the status field
    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - {self.discount}% off"

class ProductOffer(models.Model):

    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=4,decimal_places=2)
    description = models.TextField(blank=True,null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    STATUS_CHOICES = [
        ('expired', 'Expired'),
        ('active', 'Active'),
        ('upcoming', 'Upcoming')
    ]

    # Add the status field with choices and a default value
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    def __str__(self):
        return f"{self.category} - {self.discount}% off"

    # Create a function to update the status field
    def update_status(self):
        current_date = timezone.now().date()
        if self.end_date < current_date:
            self.status = 'expired'
        elif self.start_date <= current_date <= self.end_date:
            self.status = 'active'
        elif self.start_date > current_date and self.end_date > current_date:
            self.status = 'upcoming'
    
    # Override the save method to automatically update the status field
    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.product} - {self.discount}% off"

    

