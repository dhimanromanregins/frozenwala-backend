from rest_framework import serializers
from .models import Order
from menu_management.models import Item

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
from rest_framework import serializers
from .models import Order

class GroupedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'created_at', 'total_price', 'status')
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'item_photo', 'item_quantity', 'item_measurement',
                  'item_old_price', 'discount', 'item_new_price', 'status', 'category', 'created_at',
                  'deal_of_the_day', 'recommended', 'most_popular']