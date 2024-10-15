import json

import requests
from config import Config


def verify_recaptcha(response):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        'response': response,
        'secret': Config.RECAPTCHA_PRIVATE_KEY
    }
    r = requests.post(url, data=data)
    result = json.loads(r.text)

    return result