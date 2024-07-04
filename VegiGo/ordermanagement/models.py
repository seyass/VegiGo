from decimal import Decimal
from django.db import models ,transaction
from customer.models import vgUser,UserAddress
from productmanagement.models import Product

# Create your models here.

class Order(models.Model):

    ORDER_PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    PAYMENT_METHOD = [
        ('cod','Cod'),
        ('wallet','Wallet'),
        ('razorpay','Razorpay'),
    ]
    
    user = models.ForeignKey(vgUser,on_delete=models.CASCADE)
    address_info = models.JSONField()
    payment_method = models.CharField(max_length=20,choices=PAYMENT_METHOD)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    razorpayId = models.CharField(max_length=50, null=True, blank=True, default=None)
    coupon_code = models.CharField(max_length=50,null=True,blank=True,default='None')
    coupon_amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True,default=0.00)
    total_discount = models.DecimalField(max_digits=5,decimal_places=2,default=0.00)
    order_payment_status = models.CharField(max_length=20,choices=ORDER_PAYMENT_STATUS,default='pending')

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('return_requested', 'Return Requested'),
        ('returned', 'Returned'),
        ('failed','Failed'),
        ('proccessing','Proccessing'),
        ('in_transit','In transit'),
        
    ]
    PAYMENT_STATUS_CHOICES = {
        ('pending','Pending'),
        ('failed','Failed'),
        ('completed','Completed'),
    }
    
    key_product = models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_created_at = models.DateTimeField(auto_now_add=True)
    product = models.JSONField()
    image = models.ImageField(upload_to='order_items', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS_CHOICES,default='pending')
    user_cancel = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,default=0.00)

    def subtotal(self):
        return self.price * self.quantity


  

