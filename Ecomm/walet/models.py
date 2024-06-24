from django.db import models

# Create your models here.
class Walet(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    wallet_value = models.FloatField(default=0.0)