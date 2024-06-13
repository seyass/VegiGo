from django.db import models
from authentication.models import vgUser


# Create your models here.

class Branches(models.Model):

    name = models.CharField(max_length=200,unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:

        return self.name
    

class Coupon(models.Model):

    code = models.CharField(max_length=10,unique=True)
    discount_amount = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    minimum_purchase = models.IntegerField()
    used_by_users = models.ManyToManyField(vgUser,blank=True)
    
