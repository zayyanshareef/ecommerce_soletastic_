from django.db import models
from user_auth.models import *
from admin_app.models import *
from django.utils import timezone
# Create your models here.


class Cart(models.Model):
    customuser=models.ForeignKey(Custom_User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    qty=models.IntegerField(null=False,blank=False)
    size=models.IntegerField(null=False,blank=False)
    price=models.IntegerField(null=False,blank=False)
    total_price=models.IntegerField(null=False,blank=False)
    
    total_price=models.IntegerField(null=False,blank=False)

    class Meta:
        ordering = ['-id']


class Wishlist(models.Model):

    customuser=models.ForeignKey(Custom_User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

    class Meta:
        ordering =['-id']


class User_Coupon(models.Model):

    customuser=models.ForeignKey(Custom_User,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']



class Wallet_Transactions(models.Model):
    customuser = models.ForeignKey(Custom_User,on_delete=models.CASCADE)
    amount = models.IntegerField(null=False)
    resons = models.CharField(max_length=250,null=False)
    created_date = models.DateTimeField(default=timezone.now,null=False)
    add_or_pay = models.CharField(max_length=100,null=False)
    

    class Meta:
        ordering = ['-id']