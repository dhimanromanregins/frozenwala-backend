# Generated by Django 4.1.13 on 2024-04-06 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='walet',
            name='wallet_value',
            field=models.FloatField(default=0.0),
        ),
    ]
