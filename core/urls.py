# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('plaid/link-token/', views.plaid_link_token, name='plaid_link_token'),
    path('plaid/exchange-token/', views.plaid_exchange_token, name='plaid_exchange_token'),
]