"""
URL configuration for Ecomm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include('ecomApp.urls')),
    path('api/', include('backendlogin.urls')),
    path('api/', include('registration.urls')),
    path('api/', include('menu_management.urls')),
    path('api/', include('advertisement_management.urls')),
    path('api/', include('banner_management.urls')),
    path('api/', include('order.urls')),
    path('api/', include('walet.urls')),
    path('api/', include('cart.urls')),
    path('api/', include('report.urls')),
    path('api/', include('notification.urls')),
    path('api/', include('chart.urls')),

]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
