import logging

from django.shortcuts import render
from main_app import mpesa
import requests
# Create your views here.
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
def initialize_payment(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        logger.info(f"{phone} - {amount}")

        data = {
            "BusinessShortCode": mpesa.get_business_shortcode(),
            "Password": mpesa.generate_password(),
            "Timestamp": mpesa.get_current_timestamp(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": mpesa.get_business_shortcode(),
            "PhoneNumber": phone,
            "CallBackURL": mpesa.get_callback_url(),
            "AccountReference": "12345",
            "TransactionDesc": "payment for merchandise"
        }
        headers = mpesa.generate_request_headers()
        response = requests.post(mpesa.get_payment_url(), json=data, headers=headers)
        logger.debug(response.json())
        json_response = response.json()
        if 'Responsecode' in json_response:
            code = json_response['Responsecode']
            if code == '0':
                mid = json_resp['MerchantRequestID']
                cid = json_resp['CheckoutRequestID']
                logger.info(f"{mid} - {cid}")
            else:
                logger.error(f'error while initiating stk push {code}')
        elif 'errorcode' in json_response:
            errorcode = json_response['errorcode']
            logger.error(f'error code: {errorcode}')
    return render(request, 'payment.html')


@csrf_exempt
def callback(request):
    result = json.loads(request.body)
    mid = result['Body']['stkCallback']['MerchantRequestID']
    cid = result['Body']['stkCallback']['CheckoutRequestID']
    code = result['Body']['stkCallback']['ResultCode']
    logger.info(f'From Callback Result {mid} - {cid} - {code}')
    return HttpResponse({'message': 'successfully received '})
