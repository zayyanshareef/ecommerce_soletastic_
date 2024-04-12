from django.db import models
from user_auth.models import *
from django.utils import timezone
import PIL
from PIL import Image 


# Create your models here.


class Category(models.Model):
    name=models.CharField( max_length=200)
    is_deleted=models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']


class Sub_category(models.Model):

    name =models.CharField(max_length=200)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    is_deleted=models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']



class Product(models.Model):
    
    name=models.CharField(max_length=250)
    price=models.IntegerField(null=False)
    discount=models.IntegerField( null=True)
    sub_category=models.ForeignKey(Sub_category,on_delete=models.CASCADE) 
    description=models.TextField()
    is_deleted = models.BooleanField(default=False)
    image =  models.ImageField(upload_to='img/product')

    def __bool__(self):
        return  self.is_deleted
    
    def __iter__(self):
        
        return  self.id
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 500 or img.width > 700:
            output_size = (500, 700)
            img.thumbnail(output_size)
            img.save(self.image.path)
    
    class Meta:
        ordering = ['id']
    

class Product_image(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to ='img/product')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image_url.path)
        if img.height > 500 or img.width > 700:
            output_size = (500, 700)
            img.thumbnail(output_size)
            img.save(self.image_url.path)

    


class Product_size(models.Model):
    size=models.CharField(max_length=50,null=False)
    stock=models.IntegerField(null=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)



class Order(models.Model):

    ORDER_STATUS=(
        ('pending','pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded','Refunded'),
    )



    user =models.ForeignKey(Custom_User,on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100,null=False,unique=True)
    user_address = models.TextField(null=False,blank=False)
    total_amount = models.IntegerField(null=False)
    payment_type = models.CharField(max_length=100,null=False)
    status = models.CharField(max_length=100,choices=ORDER_STATUS,default='pending')
    status_date = models.DateTimeField(default=timezone.now,null=False)
    order_id = models.CharField(max_length=100,null=False,unique=True)
    created_date =models.DateTimeField(default=timezone.now,null=False)
    coupon_valid_amount = models.IntegerField(null=True)
    coupon_discount= models.IntegerField(null=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.id
        self.total_amount = int(self.total_amount)
    class Meta:
        ordering = ['-id']





class Order_items(models.Model):

    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True)
    Sub_category = models.ForeignKey(Sub_category,on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField(null=False,blank=False)
    size = models.IntegerField(null=False,blank=False)
    price = models.IntegerField(null=False,blank=False)
    total_price = models.IntegerField(null=False,blank=False)


    class Meta:
        ordering = ['-id']


class Coupon(models.Model):

    name=models.CharField(max_length=50,null=False,blank=False)
    offer_valid_amount= models.IntegerField(null=False)
    discount = models.IntegerField(null=False,blank=False)
    created_date=models.DateField(default=timezone.now,null=False)
    is_delete =models.BooleanField(default=False)

    def __int__(self):
        return self.id

    
from django.db import models
from django.contrib.auth.models import User




