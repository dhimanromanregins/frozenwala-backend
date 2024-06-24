from django.db import models
from ecomApp.models import Catagory
# Create your models here.
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    title=models.CharField(max_length=500)
    description=models.CharField(max_length=1000)
    item_photo = models.ImageField(upload_to='item_photos/')
    # item_quantity = models.PositiveIntegerField()
    # item_measurement=models.CharField(max_length=10, default='')
    item_old_price = models.FloatField()
    makingprice = models.FloatField()
    discount = models.IntegerField()
    item_new_price = models.FloatField()
    status= models.BooleanField(default=True)
    category = models.ForeignKey(Catagory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deal_of_the_day = models.BooleanField(default=False)
    recommended = models.BooleanField(default=False)
    most_popular = models.BooleanField(default=False)

    def __str__(self):
        return f"Item ID: {self.id}, Category: {self.category.name}"