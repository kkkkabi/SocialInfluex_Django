
from django.shortcuts import render, redirect
from django.conf import settings

from uuid import uuid4
import tweepy as tweepy

import requests

import json





INSTAGRAM_PAGE_ID ='61257090547'
INSTAGRAM_BUSINESS_ACCOUNT_ID ='17841461276417136'
INSTAGRAM_PAGE_ACCESS_TOKEN ='EAANVsdVkf4oBO5E6K1HuqZBvOaJLd8gVP4WUIk7TkUGiZB6zl3kvoZAm4oNrHjH43a6LVmhirBR2FfJQLLKKC7TCMOUQi9BB8uiaO27vOTZB7C1PyGYaoNsyMJuVy1r793bwAiqZCMVGtZCWGNROHQfQZCQqEZC9LSlM7DO8oCYhM1MRCtECMa8ZCQtu47rtUUEkX'

container_url = 'https://graph.facebook.com/v19.0/{}/media'.format(INSTAGRAM_BUSINESS_ACCOUNT_ID)
publish_url = 'https://graph.facebook.com/v19.0/{}/media_publish'.format(INSTAGRAM_BUSINESS_ACCOUNT_ID)

payload = {
    'image_url': "https://photographylife.com/wp-content/uploads/2014/09/Nikon-D750-Image-Samples-2.jpg",  
    'is_carousel_item': True,  
    'access_token': INSTAGRAM_PAGE_ACCESS_TOKEN  
} 

json_payload = json.dumps(payload)
res = requests.post(container_url, json_payload)
if res.status_code != 200:
    print("Failed to create an item container.")

else:
    result = json.load(res.text)
    continer_id = result.get('id')
    print("Item container created successfully:", continer_id)
