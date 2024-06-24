from rest_framework import serializers
from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
class CartGetSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.title', read_only=True)
    product_image = serializers.URLField(source='product_id.item_photo', read_only=True)
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        # Format the price to have only two digits after the decimal point
        return "{:.2f}".format(obj.price)
    class Meta:
        model = Cart
        fields = ['id', 'product_id', 'u_id', 'quantity', 'price', 'product_name', 'product_image']