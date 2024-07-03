from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser,Otp
from django.db.models import Sum
from django.db.models import Count
from django.utils.timezone import datetime, timedelta
from django.db.models.functions import TruncDate
from django.db.models import Max, Subquery, OuterRef, Window
from collections import defaultdict
from django.db.models.functions import RowNumber
from django.db.models import F
from django.shortcuts import render

from menu_management.models import Item
from django.db.models import Count, Avg
# Create your views here.
from collections import defaultdict
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, F, Window, Subquery, OuterRef
from django.db.models.functions import RowNumber
from django.shortcuts import render

@login_required(login_url='backend/login')
def dashboard(request):
    if request.method == 'GET':
        order_type = request.GET.get('order_type', None)
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)

        # Convert date strings to datetime objects if provided
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        else:  # If to_date is not provided, set it to today
            to_date = datetime.now()

        if not from_date:
            from_date = to_date - timedelta(days=30)

        queryset = Order.objects.exclude(payment_id="")

        if order_type:
            queryset = queryset.filter(pick_up=order_type)

        if from_date and to_date:
            to_date = to_date + timedelta(days=1)
            queryset = queryset.filter(created_at__range=(from_date, to_date))

        # Perform aggregation and ordering
        day_wise_report = queryset.values('order_id', 'created_at', 'total_price') \
            .annotate(
                total_items=Count('id'),
                average_price=Avg('price'),
                total_making_price=Sum(F('product_id__makingprice') * F('quantity'))
            ).order_by('order_id')

        unique_orders = {}
        total_all_orders = 0
        total_profit_amount = 0

        for entry in day_wise_report:
            order_id = entry['order_id']
            created_at = entry['created_at'].strftime('%Y-%m-%d')
            total_making_price = entry['total_making_price']
            total_price = entry['total_price']
            delivery_price = float(entry.get('delivery_price', 0))  # Use get() to avoid KeyError

            if order_id not in unique_orders:
                unique_orders[order_id] = {
                    'created_at': created_at,
                    'total_amount': total_price,
                    'total': total_price,
                    'total_making_price': total_making_price,
                    'delivery_price': delivery_price
                }
            else:
                unique_orders[order_id]['total_amount'] += total_price
                unique_orders[order_id]['total_making_price'] += total_making_price

        for entry in day_wise_report:
            order_id = entry['order_id']
            profit_amount = entry['total_price'] - unique_orders[order_id]['total_making_price'] - \
                            unique_orders[order_id]['delivery_price']
            unique_orders[order_id]['profit_amount'] = profit_amount
            unique_orders[order_id]['total_pr'] = entry['total_price']

        total_all_orders = sum(entry['total_amount'] for entry in unique_orders.values())
        total_profit_amount += sum(entry['profit_amount'] for entry in unique_orders.values())

        day_wise_report = [{'order_id': key, **value} for key, value in unique_orders.items()]

        # Filter orders based on the provided parameters
        queryset = Order.objects.exclude(payment_id="")

        # Subquery to get the latest order for each payment_id using Window function
        annotated_queryset = queryset.annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=F('payment_id'),
                order_by=F('created_at').desc()
            )
        )
        filtered_queryset = annotated_queryset.filter(row_number=1)

        if order_type:
            filtered_queryset = filtered_queryset.filter(pick_up=order_type)

        if from_date and to_date:
            to_date = to_date + timedelta(days=1)
            filtered_queryset = filtered_queryset.filter(created_at__range=(from_date, to_date))

        day_wise_report = filtered_queryset.values('created_at') \
            .annotate(total_amount=Sum('total_price')) \
            .order_by('created_at')

        unique_dates = defaultdict(lambda: {'total': 0})
        total_all_orders = 0

        for entry in day_wise_report:
            created_at = entry['created_at'].strftime('%Y-%m-%d')
            total_price = entry['total_amount']

            unique_dates[created_at]['total'] += total_price
            total_all_orders += total_price

        day_wise_report = [{'created_at': key, **value} for key, value in unique_dates.items()]

        # Retrieve total number of CustomUser
        total_custom_users = CustomUser.objects.count()

        # Retrieve total number of Item
        total_items = Item.objects.count()

        # Retrieve total number of unique payment_id of Order
        total_unique_payment_ids = Order.objects.exclude(payment_id="").values('payment_id').distinct().count()

        # Retrieve total of total_price of Order with unique payment_id
        distinct_payment_ids = Order.objects.exclude(payment_id="").values('payment_id').distinct()
        total_order_prices = 0

        for payment_id in distinct_payment_ids:
            total_order_prices += Order.objects.filter(payment_id=payment_id['payment_id']).aggregate(total_price=Sum('total_price'))['total_price']

        items = Item.objects.all().order_by('-created_at')[:5]
        orders = Order.objects.all().order_by('-created_at')

        orders_dict = {}

        for order in orders:
            if order.payment_id:
                if order.order_id not in orders_dict:
                    orders_dict[order.order_id] = order
        first_elements = [order for order in orders_dict.values()][:5]

        return render(request, 'backend/dashboard.html', {
            'ordform': first_elements,
            'items': items,
            'total_custom_users': total_custom_users,
            'total_items': total_items,
            'total_unique_payment_ids': total_unique_payment_ids,
            'total_order_prices': total_all_orders,
            'day_wise_report': day_wise_report,
            'total_profit_amount': total_profit_amount,
            'total_making': total_all_orders - total_profit_amount,
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': to_date.strftime('%Y-%m-%d'),
        })

    return render(request, 'backend/dashboard.html')
    
@login_required(login_url='backend/login')
def charts(request):
    return render(request,"backend/charts.html")

from django.contrib.auth import get_user_model  # Import get_user_model
from django.contrib.auth.models import User  # Import the User model

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
import random
# from django.contrib.auth.models import User
from django.utils import timezone

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()  # Use User model
        if user and user.is_staff:
            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Send OTP email
            subject = 'OTP for Password Change'
            message = f'Your OTP for password change is: {otp}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            # Store OTP and its creation time in database
            otp_obj, created = Otp.objects.get_or_create(user=user)
            otp_obj.otp = otp

            otp_obj.otp_created_at = timezone.now()
            otp_obj.save()

            return redirect('verify_otp')
        else:
            error = "Email does not exist or user is not authorized."
            return render(request, 'send_otp.html', {'error': error})
    return render(request, 'send_otp.html')

def verify_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email, is_staff=True).first()
        if user:
            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Send OTP email
            subject = 'OTP for Email Verification'
            message = f'Your OTP for email verification is: {otp}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            # Store OTP and its creation time in database
            otp_obj, created = Otp.objects.get_or_create(user=user)
            otp_obj.otp = otp
            otp_obj.otp_created_at = timezone.now()
            otp_obj.save()

            # Store email in session
            request.session['verified_email'] = email

            return redirect('verify_otp')
        else:
            error = "Email does not exist or user is not authorized."
            return render(request, 'backend/verify_email.html', {'error': error})
    return render(request, 'backend/verify_email.html')
from django.contrib import messages

def verify_otp(request):
    email = request.session.get('verified_email')
    if not email:
        # If email is not found in session, redirect to the verify_email page
        messages.error(request, 'Please verify your email first.')
        return redirect('verify_email')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_staff:
            otp_obj = Otp.objects.filter(user=user).first()
            if otp_obj:
                # Check if OTP matches
                if otp_obj.otp == otp_entered:
                    # Check if OTP is expired (5 minutes expiry)
                    if (timezone.now() - otp_obj.otp_created_at).total_seconds() > 300:
                        return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'OTP has expired. Please request a new OTP.'})
                    else:
                        return redirect('change_password')
                else:
                    return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'Invalid OTP. Please enter the correct OTP.'})
            else:
                return render(request, 'backend/verify_otp.html', {'email': email, 'error': 'OTP not found. Please request a new OTP.'})
        else:
            error = "Otp Does Not Match!!"
            return render(request, 'backend/verify_otp.html', {'error': error})
    return render(request, 'backend/verify_otp.html', {'email': email})
from django.contrib.auth import update_session_auth_hash

def change_password(request):
    if request.method == 'POST':
        email = request.session.get('verified_email')
        if not email:
            # If email is not found in session, redirect to the verify_email page
            messages.error(request, 'Please verify your email first.')
            return redirect('change_password')

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'backend/change_password.html')

        user = CustomUser.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, "Password changed successfully.")
            return redirect('backend/login')
        else:
            messages.error(request, "User not found.")
            return redirect('verify_email')
    return render(request, 'backend/change_password.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .models import Catagory,Stock
from django.shortcuts import render

@login_required(login_url='backend/login')
def catagory(request):
    catagoryapp=Catagory.objects.all().order_by('-id')

    context={
        'banform': catagoryapp

    }
    return render(request,'backend/catagory.html',context)
@login_required(login_url='backend/login')
def catgoryadd(request):
    if request.method == "POST":
        contact = Catagory()
        name = request.POST.get('name')
        image = request.FILES.get('image')
        contact.name = name
        contact.image = image
        contact.save()
        return redirect('catagoryapp')
    return render(request, 'backend/catgoryadd.html')
@login_required(login_url='backend/login')
def delete_item(request, myid):
    catagoryapp=Catagory.objects.get(id=myid)
    catagoryapp.delete()
    return redirect('catagoryapp')
@login_required(login_url='backend/login')
def edit_item(request, myid):
    sel_catform=Catagory.objects.get(id=myid)
    cat = Catagory.objects.all()
    context = {
        'cat': cat,
        'sel_catform':sel_catform

    }
    return render(request,'backend/catagoryedit.html',context)
@login_required(login_url='backend/login')
def update_item(request, myid):
    catagoryapp=Catagory.objects.get(id=myid)

    catagoryapp.name = request.POST.get('name')
    if 'image' in request.FILES:
        catagoryapp.image = request.FILES['image']

    catagoryapp.save()
    return redirect('catagoryapp')
@login_required(login_url='backend/login')
def view_item(request, myid):
    sel_catform = Catagory.objects.get(id=myid)
    cat = Catagory.objects.all()
    context = {
        'catform': cat,
        'sel_catform': sel_catform

    }
    return render(request, 'backend/catagoryview.html', context)
@login_required(login_url='backend/login')
def activate_catagory(request, catagory_id):
    banner = get_object_or_404(Catagory, id=catagory_id)
    banner.status = True
    banner.save()
    return redirect('catagoryapp')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_catagory(request, catagory_id):
    banner = get_object_or_404(Catagory, id=catagory_id)
    banner.status = False
    banner.save()
    return redirect('catagoryapp')  # Redirect to your banner list view
# Create your views here.
@login_required(login_url='backend/login')
def customerlist(request):
    productapp=CustomUser.objects.all()

    context={
        'banform': productapp
    }
    return render(request,'backend/customerlist.html',context)
@login_required(login_url='backend/login')
def activate_customer(request, id):
    banner = get_object_or_404(CustomUser, id=id)
    banner.status = True
    banner.save()
    return redirect('customerlist')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_customer(request, id):
    banner = get_object_or_404(CustomUser, id=id)
    banner.status = False
    banner.save()
    return redirect('customerlist')  # Redirect to your banner list view

@login_required(login_url='backend/login')
def product(request):
    productapp=Product.objects.all()

    context={
        'banform': productapp
    }
    return render(request,'backend/product.html',context)
@login_required(login_url='backend/login')
def productadd(request):
    if request.method == "POST":
        product = Product()
        stock = Stock()
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        created_date = request.POST.get('created_date')
        coupon = request.POST.get('coupon')
        openingstock=request.POST.get('openingstock')

        image = request.FILES.get('image')
        product.name = name
        product.price = price
        product.description = description
        product.created_date =created_date
        product.coupon = coupon
         # Get the selected category ID
        cat_name = request.POST.get('cat_name')

       # Get the selected category name
        category = Catagory.objects.get(name=cat_name)  # Retrieve the Category object by name
        product.cat_name = category
        product.image = image
        stock.openingstock = openingstock
        stock.item = product
        product.save()
        stock.save()

        return redirect('productapp')
    # categories = Catagory.objects.get(status=True)
    categories = Catagory.objects.all()
    return render(request, 'backend/productadd.html',{'categories': categories})
@login_required(login_url='backend/login')
def delete_product(request, myid):
    productapp=Product.objects.get(id=myid)
    productapp.delete()
    return redirect('productapp')
@login_required(login_url='backend/login')
def edit_product(request, myid):
    sel_proform=Product.objects.get(id=myid)
    pro = Product.objects.all()
    # categories = Catagory.objects.filter(status=True)
    categories = Catagory.objects.all()
    context = {

        'pro': pro,
        'sel_proform':sel_proform,
        'categories':categories

    }
    return render(request,'backend/productedit.html',context)
@login_required(login_url='backend/login')
def update_product(request, myid):
    productapp=Product.objects.get(id=myid)

    productapp.name = request.POST.get('name')
    productapp.price = request.POST.get('price')
    productapp.description = request.POST.get('description')
    productapp.created_date = request.POST.get('created_date')
    if 'image' in request.FILES:
        productapp.image = request.FILES['image']
    cat_name = request.POST.get('cat_name')  # Get the selected category name
    category = Catagory.objects.get(name=cat_name)  # Retrieve the Category object by name
    productapp.cat_name = category

    productapp.save()

    return redirect('productapp')
@login_required(login_url='backend/login')
def view_product(request, myid):
    sel_proform = Product.objects.get(id=myid)
    pro = Product.objects.all()
    context = {
        'proform': pro,
        'sel_proform': sel_proform

    }
    return render(request, 'backend/productview.html', context)
@login_required(login_url='backend/login')
def activate_product(request, product_id):
    banner = get_object_or_404(Product, id=product_id)
    banner.status = True
    banner.save()
    return redirect('productapp')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_product(request, product_id):
    banner = get_object_or_404(Product, id=product_id)
    banner.status = False
    banner.save()
    return redirect('productapp')  # Redirect to your banner list view
# Create your views here.
from .models import CustomerCoupon
@login_required(login_url='backend/login')
def add_customer_coupon(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customerName')
        occasion_name = request.POST.get('occasionName')
        start_date = request.POST.get('startDate')
        image = request.FILES.get('image')

        expire_date = request.POST.get('expireDate')
        coupon_value = request.POST.get('couponValue')
        coupon_type = request.POST.get('couponType')
        description = request.POST.get('description')
        # Assuming 'occasion_name' is the name of the occasion for which the coupon is issued

        customer_coupon = CustomerCoupon(
            coupon=customer_name,
            occasion=occasion_name,
            expire_date=expire_date,
            start_date=start_date,
            coupon_value=coupon_value,
            coupon_type=coupon_type,
            description=description,
            image=image
        )
        customer_coupon.save()

        return redirect('customer_couponlist')  # Redirect to the desired page after submission

    return render(request, 'backend/add_customer_coupon.html')
@login_required(login_url='backend/login')
def customer_couponlist(request):
    coupons = CustomerCoupon.objects.all()
    return render(request, 'backend/customercouponlist.html', {'coupons': coupons})
from django.shortcuts import get_object_or_404
@login_required(login_url='backend/login')
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(CustomerCoupon, pk=coupon_id)
    coupon.delete()
    # Optionally, add a success message or redirect to a different page
    return redirect('customer_couponlist')
@login_required(login_url='backend/login')
def activate_coupon(request, coupon_id):
    banner = get_object_or_404(CustomerCoupon, id=coupon_id)
    banner.status = True
    banner.save()
    return redirect('customer_couponlist')  # Redirect to your banner list view
@login_required(login_url='backend/login')
def deactivate_coupon(request, coupon_id):
    banner = get_object_or_404(CustomerCoupon, id=coupon_id)
    banner.status = False
    banner.save()
    return redirect('customer_couponlist')  # Redirect to your banner list view








from .models import DeliveryCharge
@login_required(login_url='backend/login')
def charge(request):
    productapp=DeliveryCharge.objects.all()

    context={
        'banform': productapp
    }
    return render(request,'backend/chargelist.html',context)
@login_required(login_url='backend/login')
def chargeadd(request):
    if request.method == "POST":
        product = DeliveryCharge()
        charge = request.POST.get('charge')

        product.charge = charge

        product.save()

        return redirect('chargeapp')
    # categories = Catagory.objects.get(status=True)
    return render(request, 'backend/add_charge.html')
@login_required(login_url='backend/login')
def delete_charge(request, myid):
    productapp=DeliveryCharge.objects.get(id=myid)
    productapp.delete()
    return redirect('chargeapp')
@login_required(login_url='backend/login')
def edit_charge(request, myid):
    sel_proform=DeliveryCharge.objects.get(id=myid)
    pro = DeliveryCharge.objects.all()
    # categories = Catagory.objects.filter(status=True)
    context = {

        'pro': pro,
        'sel_proform':sel_proform,

    }
    return render(request,'backend/edit_charge.html',context)
@login_required(login_url='backend/login')
def update_charge(request, myid):
    productapp=DeliveryCharge.objects.get(id=myid)

    productapp.charge = request.POST.get('charge')

    productapp.save()

    return redirect('chargeapp')
@login_required(login_url='backend/login')
def stock(request):
    catagoryapp=Stock.objects.all()

    context={
        'banform': catagoryapp

    }

    return render(request,'backend/inventory_list.html',context)
@login_required(login_url='backend/login')
def edit_stock(request, myid):
    sel_proform=Stock.objects.get(id=myid)
    pro = Stock.objects.all()
    # categories = Catagory.objects.filter(status=True)
    context = {

        'pro': pro,
        'item':sel_proform,

    }
    return render(request,'backend/edit_inventory.html',context)
@login_required(login_url='backend/login')
def update_stock(request,stock_id):
    if request.method == 'POST':
        openingstock = request.POST.get('openingstock')

        try:
            stock = Stock.objects.get(id=stock_id)
            stock.openingstock = openingstock
            stock.save()

            messages.success(request, 'Stock updated successfully.')
        except Stock.DoesNotExist:
            messages.error(request, 'Stock does not exist.')
        except Exception as e:
            messages.error(request, str(e))

    return redirect('stock')
@login_required(login_url='backend/login')
def update_all_stock(request):
    if request.method == 'POST':

        for key, value in request.POST.items():
            if key.startswith('openingstock_'):
                stock_id = key.split('_')[1]
                try:
                    stock = get_object_or_404(Stock, pk=stock_id)
                    stock.openingstock = value
                    stock.save()
                except Exception as e:
                    # Handle exceptions as needed
                    pass
    return redirect('stock')
@login_required(login_url='backend/login')
def allstock(request):
    catagoryapp=Stock.objects.all()

    context={
        'banform': catagoryapp

    }

    return render(request,'backend/allinventory_list.html',context)
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Stock
from .serializers import StockSerializer

class StockListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return StockSerializer

    def get_queryset(self):
        queryset = Stock.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(item_id=product_id)
        return queryset


from order.models import Order
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def count_pending_orders():
    """
    Counts the number of pending orders.
    """
    pending_orders_count = Order.objects.filter(status='1').count()

    return pending_orders_count
from django.db.models import Q
@csrf_exempt  # Add this decorator if you're not handling CSRF tokens for this view
def pending_orders_count(request):
    """
    View to return the count of pending orders.
    """
    pending_orders_count = Order.objects.filter(status='1').exclude(Q(payment_id=None) | Q(payment_id='')).values('order_id').distinct().count()
    data = {'pending_orders_count': pending_orders_count}
    return JsonResponse(data)


def render_order_dropdown(request):
    """
    Renders order details in a dropdown menu.
    """
    # Fetch the orders
    orders = Order.objects.filter(status='1')[:5]  # Fetch the first 5 orders

    # Serialize order details
    serialized_orders = [{'id': order.id, 'status': order.status, 'created_at': order.created_at} for order in orders]

    # Prepare JSON response data
    data = {'orders': serialized_orders}

    # Return JSON response
    return JsonResponse(data)

from rest_framework import generics
from .models import CustomerCoupon
from .serializers import CustomerCouponSerializer
from datetime import date

class CouponList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = CustomerCouponSerializer

    def get_queryset(self):
        today = date.today()
        return CustomerCoupon.objects.filter(start_date__lte=today, expire_date__gte=today)





