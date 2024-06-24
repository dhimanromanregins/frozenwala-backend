from django.urls import path
from .views import *
urlpatterns = [
    path('api/wallet/', WalletAPIView.as_view(), name='wallet_api'),
    path('api/save_wallet_transaction/', UpdateWallet.as_view(), name='save_wallet_transaction'),

    # Other URL patterns...
]
