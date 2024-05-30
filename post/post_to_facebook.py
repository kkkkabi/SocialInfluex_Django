from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import tweepy as tweepy
import requests
import json


FACEBOOK_PAGE_ACCESS_TOKEN = settings.FACEBOOK_PAGE_ACCESS_TOKEN
FACEBOOK_PAGE_ID = settings.FACEBOOK_PAGE_ID
POST_URL = "https://graph.facebook.com/v19.0/{}/feed".format(FACEBOOK_PAGE_ID)
IMAGE_URL = "https://graph.facebook.com/v19.0/{}/photos".format(FACEBOOK_PAGE_ID)

def post_to_facebook(message: str, image_urls: List[str]):
    uploaded_photo_ids = upload_images_to_facebook(image_urls)
    if not uploaded_photo_ids:
        print("No images uploaded to Facebook")
        payload = {
        'message': message,
        'access_token': FACEBOOK_PAGE_ACCESS_TOKEN,
        }
    
    else: 
        payload = {
            'message': message,
            'attached_media': json.dumps([{"media_fbid": photo_id} for photo_id in uploaded_photo_ids]),
            'access_token': FACEBOOK_PAGE_ACCESS_TOKEN,
        }
    response = requests.post(POST_URL, data=payload)
    if response.status_code == 200:
        print("Posted to Facebook successfully")
    else:
        print(f"Failed to post to Facebook: {response.text}")
   


def upload_images_to_facebook(images: List[bytes]) -> List[str]:
    uploaded_photo_ids = []
    for image in images:
        response = upload_image_to_facebook(image)
        if response and 'id' in response:
            uploaded_photo_ids.append(response['id'])
    return uploaded_photo_ids

def upload_image_to_facebook(image: bytes) -> Optional[dict]:
    payload = {
        'access_token': FACEBOOK_PAGE_ACCESS_TOKEN,
        'published': 'false',  # Change to 'true' if you want to publish the photo immediately
    }
    files = {
        'source': image,
    }
    response = requests.post(IMAGE_URL, data=payload, files=files)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to upload image: {response.text}")
        return None
    
