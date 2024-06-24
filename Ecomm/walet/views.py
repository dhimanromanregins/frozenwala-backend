from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from ecomApp.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
class WalletAPIView(View):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'User ID parameter is missing'}, status=400)

        try:
            user = CustomUser.objects.get(pk=user_id)
            wallet_value = user.walet
            return JsonResponse({'wallet_value': wallet_value})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ecomApp.models import CustomUser
from .models import Walet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

class UpdateWallet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('user_id')

        # Check if user exists
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        wallet, created = Walet.objects.get_or_create(user_id=user.id)

        # Get amount to subtract from the wallet
        try:
            amount_to_subtract = user.walet
        except AttributeError:
            return Response({"error": "Wallet amount not provided."}, status=status.HTTP_400_BAD_REQUEST)


        wallet.wallet_value += amount_to_subtract
        wallet.save()
        user.walet-=amount_to_subtract
        user.save()
        return Response({"success"})