from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Address

admin.site.register(Address)