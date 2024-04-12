
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Custom_User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    username = models.CharField(max_length=30, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    ph_no = models.CharField(max_length=15, blank=False)
    wallet_bal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Add any additional required fields

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )


   
    
    def __str__(self):
        return self.email

    def __int__(self):
        return self.id 

    class Meta:
        ordering = ['-id']
    





class User_Address(models.Model):
    name=models.CharField(max_length=100,null=False)
    email=models.EmailField(null=False,blank=False)
    phone=models.CharField(max_length=100,null=False,blank=False)
    house=models.TextField(null=False,blank=False)
    street=models.TextField(null=False,blank=False)
    city=models.TextField(null=False,blank=False)
    state=models.TextField(null=False,blank=False)
    country=models.TextField(null=False,blank=False)
    pin_code=models.TextField(null=False,blank=False)
    location=models.TextField(null=False,blank=False)
    customuser=models.ForeignKey(Custom_User,on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']


