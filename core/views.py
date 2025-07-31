# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.conf import settings
import plaid
import logging
from datetime import date  # Added for date objects

# Configure logging
logger = logging.getLogger(__name__)

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

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

# Store access tokens (temporary in-memory solution)
access_tokens = {}

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
            return render(request, 'core/register.html', {'form': form})  # Fixed syntax
    return render(request, 'core/register.html', {'form': UserCreationForm()})

def dashboard_view(request):
    if request.user.is_authenticated:
        return render(request, 'core/dashboard.html', {'username': request.user.username})
    return redirect('core:login')

def plaid_link_token(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    try:
        logger.info(f"Generating link token with client_id={settings.PLAID_CLIENT_ID[:4]}..., PLAID_ENV={settings.PLAID_ENV}, user_id={str(request.user.id)}")
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
            logger.info(f"Exchanging public token: {public_token[:4]}..., user_id={str(request.user.id)}")
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            exchange_response = client.item_public_token_exchange(exchange_request)
            access_token = exchange_response['access_token']
            user_id = str(request.user.id)
            access_tokens[user_id] = access_token  # Ensure token is saved
            logger.info(f"Public token exchanged successfully for user {user_id}, access_token={access_token[:4]}... saved")
            return JsonResponse({'status': 'success', 'access_token': access_token})
        except plaid.ApiException as e:
            logger.error(f"Plaid API error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def plaid_get_transactions(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    user_id = str(request.user.id)
    logger.info(f"Checking transactions for user_id={user_id}, access_tokens={access_tokens}")
    if user_id not in access_tokens or not access_tokens[user_id]:
        return JsonResponse({'error': 'No access token available. Please connect a bank account first.'}, status=400)
    try:
        access_token = access_tokens[user_id]
        request_data = TransactionsGetRequest(
            access_token=access_token,
            start_date=date(2024, 7, 29),  # Converted to date object
            end_date=date(2025, 7, 29),    # Converted to date object
            options=TransactionsGetRequestOptions()
        )
        response = client.transactions_get(request_data)
        transactions = response['transactions']
        logger.info(f"Fetched {len(transactions)} transactions for user {user_id}")
        return JsonResponse({'transactions': [{'name': t.name, 'amount': t.amount, 'date': t.date} for t in transactions]})
    except plaid.ApiException as e:
        logger.error(f"Plaid API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)