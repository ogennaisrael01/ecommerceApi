
import requests
import json
from django.conf import settings


def check_out(payload):

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        'https://api.paystack.co/transaction/initialize',
        headers=headers, 
        data=json.dumps(payload)
    )
    response_data = response.json() 

    if response_data.get("status") == True:
        return ({"success": True, "message": response_data["data"]["authorization_url"]})
    else:
        return ({"success": False, "message": "Failed to initiate payments, Please try again later"})
    