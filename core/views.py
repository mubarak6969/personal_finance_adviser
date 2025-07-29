# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.conf import settings
import plaid
import logging

# Configure logging
logger = logging.getLogger(__name__)

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Plaid client configuration
env_map = {
    'sandbox': 'https://sandbox.plaid.com',
    'development': 'https://development.plaid.com',
    'production': 'https://production.plaid.com'
}
client = plaid_api.PlaidApi(plaid_api.ApiClient(
    configuration=plaid.Configuration(
        host=env_map.get(settings.PLAID_ENV.strip(), 'https://sandbox.plaid.com'),
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET,
        }
    )
))

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:login')
        else:
            return render(request, 'core/register.html', {'form': form})
    return render(request, 'core/register.html', {'form': UserCreationForm()})

def dashboard_view(request):
    if request.user.is_authenticated:
        return render(request, 'core/dashboard.html', {'username': request.user.username})
    return redirect('core:login')

def plaid_link_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    try:
        logger.info(f"Generating link token with client_id={settings.PLAID_CLIENT_ID[:4]}..., PLAID_ENV={settings.PLAID_ENV}")
        request_data = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(request.user.id)),
            client_name="Personal Finance Adviser",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en"
        )
        response = client.link_token_create(request_data)
        logger.info("Link token generated successfully")
        return JsonResponse({'link_token': response['link_token']})
    except plaid.ApiException as e:
        logger.error(f"Plaid API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

def plaid_exchange_token(request):
    if request.method == 'POST' and request.user.is_authenticated:
        public_token = request.POST.get('public_token')
        try:
            logger.info(f"Exchanging public token: {public_token[:4]}...")
            exchange_request = plaid.model.ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            exchange_response = client.item_public_token_exchange(exchange_request)
            access_token = exchange_response['access_token']
            logger.info("Public token exchanged successfully")
            # Store access_token in your database (not implemented here)
            return JsonResponse({'status': 'success', 'access_token': access_token})
        except plaid.ApiException as e:
            logger.error(f"Plaid API error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)