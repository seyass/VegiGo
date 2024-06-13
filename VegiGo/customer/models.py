from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from authentication.models import vgUser
from productmanagement.models import Product,ProductOffer,CategoryOffer
from vgadmin.models import Branches,Coupon
# Create your models here.


class UserAddress(models.Model):
    HOME = 'Home'
    WORK = 'Work'
    OTHER = 'Other'
    
    ADDRESS_TYPE_CHOICES = [
        (HOME, 'Home'),
        (WORK, 'Work'),
        (OTHER, 'Other'),
    ]
    user = models.ForeignKey(vgUser, on_delete=models.CASCADE, related_name='addresses')
    firstname = models.CharField(max_length=65)
    lastname = models.CharField(max_length=65)
    phone_number = models.CharField(max_length=10)
    street_address = models.CharField(max_length=100)
    landmark = models.CharField(max_length=65)
    pincode = models.PositiveIntegerField()
    city = models.CharField(max_length=50)
    district = models.ForeignKey(Branches,on_delete=models.CASCADE)
    address_type = models.CharField(max_length=10,choices=ADDRESS_TYPE_CHOICES,default=HOME)
    constraints = [
            models.UniqueConstraint(
                fields=['firstname','lastname','user', 'street_address', 'pincode', 'city', 'district','phone_number'],
                name='unique_address_per_user'
            )
        ]

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.district}, {self.pincode}"

########### Cart ###########  

class Cart(models.Model):
    user = models.OneToOneField(vgUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Branches, on_delete=models.CASCADE,null=True,blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    select_coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE,blank=True,null=True)

    def is_coupon_valid(self):
        if not self.select_coupon:
            return False
        items = self.items.all()
        if self.select_coupon.end_date < timezone.now().date() or self.select_coupon.start_date > timezone.now().date():
            self.select_coupon = None
            return False
        for item in items:
            if item.total_price < self.select_coupon.discount_amount:
                self.select_coupon = None
                return False
            if self.sub_total >= self.select_coupon.minimum_purchase:
                return True
            else:
                self.select_coupon = None
                return False
        

    def calculate_total_price(self):
        total_price = sum(item.total_price for item in self.items.all())
        self.sub_total = total_price
        if self.select_coupon and self.is_coupon_valid():
            if self.select_coupon.discount_amount > 0:
                self.sub_total -= self.select_coupon.discount_amount
            else:
                self.sub_total = total_price
        else:
            self.select_coupon = None  # Remove the coupon if it's not valid
        self.save()
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_quantity = models.PositiveIntegerField(default=0,blank=True,null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.product.special_discount * self.quantity
        self.cart.calculate_total_price()
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.username}"
    
########### Wishlist ###########

class Wishlist(models.Model):

    user = models.ForeignKey(vgUser,on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

class WishlistItem(models.Model):

    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

########### Wallet ###########

class Wallet(models.Model):

    user = models.OneToOneField(vgUser,on_delete=models.CASCADE,related_name='wallet')
    amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    previous_balance = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    last_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s wallet"

class WalletHistory(models.Model):

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='wallet_history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.amount} on {self.timestamp}"
 
