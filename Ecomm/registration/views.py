# views.py
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
# from django_otp import devices_for_user
# from .serializers import RegistrationSerializer
from ecomApp.models import CustomUser,Otp
import random
from django.utils import timezone
import json
# views.py
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
User = get_user_model()
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer,ProfileSerializer,ProfileUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# @api_view(['POST'])
# def register_user(request):
#     if request.method == 'POST':
#         serializer = UserSerializer(data=request.data)
#         try:
#             if serializer.is_valid():
#                 # Hash the password before saving
#                 password = make_password(serializer.validated_data.get('password'))
#                 serializer.validated_data['password'] = password
#                 user = serializer.save()
#                 return Response({"message": "Registration successful!"}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except CustomUser.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# @api_view(['POST'])
# def login_user(request):
#     if request.method == 'POST':
#         phone_number = request.data.get('phone_number')
#         password = request.data.get('password')
#         try:
#             user = CustomUser.objects.get(phone_number=phone_number)
#         except CustomUser.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         if check_password(password, user.password):
#             return Response({"message": "Login successful!","user_id":user.id,"status":"success"}, status=status.HTTP_200_OK)
#         else:
#             # return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

AUTH_USER_MODEL = 'ecomApp.CustomUser'



class RegistrationView(APIView):
    def post(self, request):
        request_data = json.loads(request.body.decode('utf-8'))

        serializer = CustomUserSerializer(data=request_data)  # Use request_data instead of request.data
        print(request_data, "============")
        if serializer.is_valid():

            phone_number = request_data.get('phone_number')  # Assuming phone_number is in request data
            otp_code = request_data.get('otp_value')  # Assuming OTP code is in request data
            name = request_data.get('name')  # Assuming name is in request data

            # Verify OTP for the given phone number
            try:
                otp_instance = Otp.objects.get(phone_number=phone_number, otp=otp_code)
            except Otp.DoesNotExist:
                return Response({'error': 'Invalid OTP'}, status=400)

            # OTP verification successful, proceed with user registration
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            # Delete the OTP record
            otp_instance.delete()

            response_data = {
                'status': 'success',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)


from rest_framework.permissions import AllowAny


class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def post(self, request):
        request_data = json.loads(request.body.decode('utf-8'))
        phone_number = request_data.get('phone_number')
        otp = request_data.get('otp_value')
        registration_id = request_data.get('registration_id', '')

        # Verify OTP for the given phone number
        try:
            otp_instance = Otp.objects.get(phone_number=phone_number, otp=otp)
        except Otp.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=400)

        # OTP verification successful, authenticate the user using phone number
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=401)

        if user is not None:
            user.otp_value = otp

            # Authentication successful, generate tokens
            refresh = RefreshToken.for_user(user)
            if registration_id:
                # Update registration_id in CustomUser model
                user_profile = CustomUser.objects.get(id=user.id)
                user_profile.registration_id = registration_id
                user_profile.save()

            user.registration_id = registration_id
            # Update otp_value in CustomUser model
            user.otp_value = otp  # Assuming you have a field named 'otp_value' in your CustomUser model
            user.save()

            # Delete the OTP instance
            otp_instance.delete()

            response_data = {
                'user_id': user.id,
                'status': 'success',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=200)
        else:
            # Authentication failed
            return Response({'error': 'Invalid credentials'}, status=401)
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Address
from .serializers import AddressSerializer
from rest_framework.permissions import IsAuthenticated

class AddressList(APIView):
    permission_classes = [AllowAny]  # Allow access to all users

    def get(self, request):
        try:
            # Get the user_id from query parameters
            user_id = request.query_params.get('user_id')

            # Check if user_id parameter is provided
            if user_id is None:
                return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve addresses associated with the user
            addresses = Address.objects.filter(user_id=user_id)

            # Serialize the addresses data
            serializer = AddressSerializer(addresses, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # Accessing data using request.data.get()
        name = request.data.get('newname')
        phone = request.data.get('phone')
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        country = request.data.get('country')
        zip_code = request.data.get('zip_code')
        user_id = request.data.get('user_id')

        # Check if user_id is provided and if it is a valid user ID
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid User ID."}, status=400)

        # Create the Address object
        address_obj = Address.objects.create(
            newname=name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
            status=1,
            user_id=user
        )

        return Response({"message": "Address created successfully."}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_delivery_time(request):

    address_id = request.data.get('address_id')
    new_delivery_time = request.data.get('delivery_time')

    if not address_id:
        return Response({"error": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        address = Address.objects.get(pk=address_id)
    except Address.DoesNotExist:
        return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

    if new_delivery_time:
        address.delivery_time = new_delivery_time
        address.save()
        return Response({"message": "Delivery time updated successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Delivery time not provided."}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    """
    API endpoint for user profiles.
    """

    def get(self, request):
        """
        Retrieve a specific user profile by user_id.
        """
        user_id = request.query_params.get('user_id')
        try:
            profile = CustomUser.objects.get(pk=user_id)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Update a user profile.
        """
        user_id = request.data.get('user_id')
        try:
            profile = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Extract data from request
        name = request.data.get('name', "")
        email = request.data.get('email', "")
        bio = request.data.get('bio', "")
        profile_photo = request.FILES.get('profile_photo', "")  # Get the file from request.FILES

        # Update profile fields if provided
        if name is not None:
            profile.name = name
        if email is not None:
            profile.email = email
        if bio is not None:
            profile.bio = bio
        if profile_photo is not None:
            profile.profile_photo = profile_photo


        profile.save()
        return Response({"success": "Profile updated successfully"}, status=status.HTTP_200_OK)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404



class SignOutAPI(APIView):
    """
    API endpoint for user sign-out.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Retrieve the user_id from query parameters
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user object
        user = get_object_or_404(CustomUser, id=user_id)

        # Perform any additional checks if needed (e.g., verify user's identity)

        # Perform the logout action
        logout(request)

        return Response({"message": "User successfully signed out."}, status=status.HTTP_200_OK)

class DeleteAccountAPI(APIView):
    """
    API endpoint for user account deletion.
    """
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        # Retrieve the user_id from query parameters
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user object
        user = get_object_or_404(CustomUser, id=user_id)

        # Perform any additional checks if needed (e.g., verify user's identity)

        # Delete the user account
        user.delete()

        return Response({"message": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


import urllib.request
import urllib.parse


import urllib.request
import urllib.parse

import random
import string
import urllib.request
import urllib.parse


import random
import string
import urllib.request
import urllib.parse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import urllib.request

import urllib.request
import urllib.parse
import random
import string


import urllib.request
import urllib.parse
import random
import string

def generate_otp(length=6):
    # Generate a random OTP of specified length
    otp = ''.join(random.choices(string.digits, k=length))
    return otp


@csrf_exempt
def sendSMS(apikey, numbers, sender, message):
    data = urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,'message': message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request,data)
    fr = f.read()
    return (fr)

# Example usage
# Example usage
# apikey = "NGI0ZjQzMzA2MTZjNjc1NDUzNTA3MDQ1NGI1ODczNWE="
# sender_name = "FRZWLA"
# recipient_number = '917980750314'  # Make sure to pass the phone number as a string
# otp = generate_otp()
# messsage = f'Your OTP is: {otp}'
# resp = send_otp(apikey,918123456789,'Jims Autos','This is your message')
# print(resp)
@csrf_exempt
def send_sms(request):
    if request.method == 'POST':
        # Extract the parameters from the request
        apikey = "NGI0ZjQzMzA2MTZjNjc1NDUzNTA3MDQ1NGI1ODczNWE="
        sender_name = "FRZWLA"
        # recipient_number = request.POST.get('recipient_number')  # Extract from request
        request_data = json.loads(request.body.decode('utf-8'))
        recipient_number = request_data.get('phone_number')
        otp = generate_otp()
        message = f'{otp} is your signin OTP for Frozenwala account. Please apply this within 2min.'
        otp_instance, created = Otp.objects.get_or_create(phone_number=recipient_number)

        # If the record already exists, update the OTP value
        if not created:
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()
        # If the record doesn't exist, create a new OTP record
        else:
            otp_instance.otp = otp
            otp_instance.otp_created_at = timezone.now()
            otp_instance.save()        # Call the send_otp function
        response = sendSMS(apikey, recipient_number, sender_name, message)

        # Return a JSON response
        return JsonResponse({ 'status': 'success'})
    else:
        # Return an error response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=400)
