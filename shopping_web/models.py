from distutils.command.upload import upload
from email.policy import default
from itertools import product
from django.db import models
from category.models import Category
from django.utils.timezone import now
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category,on_delete = models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)
    is_sale = models.BooleanField()
    image = models.ImageField(upload_to='product', blank=True)
    star = models.IntegerField(default=0)
    description = models.CharField(blank=True, null=True, max_length=1000)

    def __str__(self):
        return self.product_name


class VisitorOrderItem(models.Model):    
    session_id = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default=0)

    
class MemberOrder(models.Model):    
    customer = models.ForeignKey(User, on_delete = models.CASCADE)
    transaction_id = models.IntegerField(blank=True, null=True)
    date_ordered = models.DateField(default=now)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    tracking_number = models.CharField(max_length=15)


class MemberOrderItem(models.Model):    
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    order = models.ForeignKey(MemberOrder, on_delete = models.CASCADE)
