
from django.db import models
from django.contrib.auth.models import User
from ecomApp.models import CustomUser
from ecomApp.models import Catagory
from ecomApp.models import Product
from django.conf import settings
from menu_management.models import Item

class Order(models.Model):

    id = models.AutoField(primary_key=True)
    order_id=models.CharField(max_length=50)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)#made CustomUser later
    product_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    couponcode = models.CharField(max_length=50)
    status = models.IntegerField()
    quantity=models.IntegerField()
    price = models.FloatField()
    total_price = models.FloatField()
    payment_id = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    newname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    delivery_time=models.CharField(max_length=50)
    order_item_id=models.CharField(max_length=50)

    dicounted_price=models.CharField(max_length=50)
    walet_value=models.CharField(max_length=50)
    pick_up=models.CharField(max_length=50)
    previous_price=models.CharField(max_length=50)
    delivery_price=models.CharField(max_length=50)

    def __str__(self):
        return  f"{self.user_id}"
