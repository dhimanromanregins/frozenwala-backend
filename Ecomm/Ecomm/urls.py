from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('base/admin/', admin.site.urls),
    path('base/', include('ecomApp.urls')),
    path('base/', include('backendlogin.urls')),
    path('base/', include('registration.urls')),
    path('base/', include('menu_management.urls')),
    path('base/', include('advertisement_management.urls')),
    path('base/', include('banner_management.urls')),
    path('base/', include('order.urls')),
    path('base/', include('walet.urls')),
    path('base/', include('cart.urls')),
    path('base/', include('report.urls')),
    path('base/', include('notification.urls')),
    path('base/', include('chart.urls')),

]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
