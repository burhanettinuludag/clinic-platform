"""
iyzico ödeme entegrasyonu servisi.
Sandbox ve production modlarını destekler.
"""

import hashlib
import hmac
import base64
import json
import random
import string
from decimal import Decimal

import requests
from django.conf import settings


class IyzicoService:
    """iyzico API ile etkileşim servisi."""

    def __init__(self):
        self.api_key = settings.IYZICO_API_KEY
        self.secret_key = settings.IYZICO_SECRET_KEY
        self.base_url = settings.IYZICO_BASE_URL

    def _generate_random_string(self, length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _make_auth_header(self, uri, body_str=''):
        random_header = self._generate_random_string(8)
        hash_str = f'{self.api_key}{random_header}{self.secret_key}{body_str}'
        sha256_hash = hashlib.sha256(hash_str.encode('utf-8')).hexdigest()
        auth_str = f'apiKey:{self.api_key}&randomHeaderValue:{random_header}&signature:{sha256_hash}'
        b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        return f'IYZWS {b64}'

    def _make_request(self, method, endpoint, data=None):
        url = f'{self.base_url}{endpoint}'
        body_str = json.dumps(data, separators=(',', ':')) if data else ''

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': self._make_auth_header(endpoint, body_str),
            'x-iyzi-rnd': self._generate_random_string(8),
        }

        if method == 'POST':
            response = requests.post(url, data=body_str, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)

        return response.json()

    def create_checkout_form(self, order, user, callback_url):
        """
        iyzico Checkout Form oluşturur.
        Kullanıcı bu form üzerinden ödeme yapar.
        """
        conversation_id = str(order.id)[:20]

        # Buyer bilgileri
        buyer = {
            'id': str(user.id),
            'name': user.first_name or 'Ad',
            'surname': user.last_name or 'Soyad',
            'email': user.email,
            'identityNumber': '11111111111',  # TC kimlik - gerçek ortamda kullanıcıdan alınacak
            'registrationAddress': order.billing_address or 'Türkiye',
            'city': order.billing_city or 'Istanbul',
            'country': order.billing_country or 'Turkey',
            'ip': order.ip_address or '85.34.78.112',
        }

        # Adres bilgileri
        address = {
            'contactName': f'{user.first_name} {user.last_name}',
            'city': order.billing_city or 'Istanbul',
            'country': order.billing_country or 'Turkey',
            'address': order.billing_address or 'Türkiye',
        }

        # Sepet kalemleri
        basket_items = []
        for item in order.items.select_related('product'):
            basket_items.append({
                'id': str(item.product.id) if item.product else str(item.id),
                'name': item.product_name,
                'category1': 'Software',
                'itemType': 'VIRTUAL',
                'price': str(item.unit_price * item.quantity),
            })

        data = {
            'locale': 'tr',
            'conversationId': conversation_id,
            'price': str(order.total_amount),
            'paidPrice': str(order.total_amount),
            'currency': 'TRY',
            'basketId': order.order_number,
            'paymentGroup': 'PRODUCT',
            'callbackUrl': callback_url,
            'enabledInstallments': [1, 2, 3, 6],
            'buyer': buyer,
            'shippingAddress': address,
            'billingAddress': address,
            'basketItems': basket_items,
        }

        result = self._make_request('POST', '/payment/iyzi-pos/checkoutform/initialize/auth', data)
        return result

    def retrieve_checkout_form(self, token):
        """
        Ödeme sonucunu token ile sorgular.
        """
        data = {
            'locale': 'tr',
            'token': token,
        }
        result = self._make_request('POST', '/payment/iyzi-pos/checkoutform/auth/ecom/detail', data)
        return result

    def refund_payment(self, payment_id, amount, ip='85.34.78.112'):
        """
        Ödeme iadesi yapar.
        """
        conversation_id = self._generate_random_string(12)
        data = {
            'locale': 'tr',
            'conversationId': conversation_id,
            'paymentTransactionId': payment_id,
            'price': str(amount),
            'currency': 'TRY',
            'ip': ip,
        }
        result = self._make_request('POST', '/payment/refund', data)
        return result


iyzico_service = IyzicoService()
