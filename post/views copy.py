from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.conf import settings

import tweepy as tweepy
import requests
import os
from datetime import datetime

from .models import UploadImages
from .post_to_instagram import post_to_instagram
from .post_to_facebook import post_to_facebook

from PIL import Image, ImageDraw, ImageFont
import textwrap

import http.server
import socketserver
import threading
import subprocess
import time
import json

IMAGE_PATH = settings.MEDIA_ROOT
FACEBOOK_PAGE_ACCESS_TOKEN = settings.FACEBOOK_PAGE_ACCESS_TOKEN
FACEBOOK_PAGE_ID = settings.FACEBOOK_PAGE_ID

INSTAGRAM_BUSINESS_ACCOUNT_ID = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
INSTAGRAM_PAGE_ACCESS_TOKEN = settings.INSTAGRAM_PAGE_ACCESS_TOKEN

TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET_KEY = settings.TWITTER_CONSUMER_SECRET_KEY
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

# https://facebook-sdk.readthedocs.io/en/latest/api.html

def post_to_selected_platforms(request):
    if request.method == "POST":
        message = request.POST.get('message', '')
        image_files = request.FILES.getlist('uploadFiles')  # Retrieve uploaded images
        selected_platforms = request.POST.getlist('platforms')  # get platforms list

        # # Start a simple HTTP server in a new thread
        # PORT = 3000
        # Handler = http.server.SimpleHTTPRequestHandler
        # httpd = socketserver.TCPServer(("", PORT), Handler)
        # thread = threading.Thread(target=httpd.serve_forever)
        # thread.start()

        # # Start ngrok
        # ngrok = subprocess.Popen(["ngrok", "http", str(PORT)], stdout=subprocess.PIPE)

        # # Give ngrok time to start up
        # time.sleep(2)

        # Get the public URL from ngrok
        # resp = requests.get("http://localhost:4040/api/tunnels")
        # public_url = resp.json()["tunnels"][0]["public_url"]
        image_bytes_list = []  # Store the image bytes
        image_path_list = []
        image_urls = []

        if len(image_files) == 0:
            new_img = create_text_image(message)
            file_name = os.path.basename(new_img)
            print(new_img)
            img_url = f"{public_url}/media/instagram_images/{file_name}"
            print("img_url",img_url)
            image_urls.append(img_url)
        
        else:

            for image in image_files:
                # create image bytes for posting to facebook
                image_bytes = image.read()  # Read the image as bytes
                image_bytes_list.append(image_bytes)
                print("image",image)

                # Create a new instance of UploadedFile model, and save image in post_images folder
                image_instance = UploadImages.objects.create(image = image)
                image_instance.save()
                print("image_instance",image_instance)
                image_path_list.append(image_instance)

                # create image url for posting to instagram
                file_name = os.path.basename(image_instance.image.name) # get the file name

                img_url = f"{public_url}/media/post_images/{file_name}"
                print("img_url",img_url)
                time.sleep(1)

                image_urls.append(img_url)
            print("image_urls",image_urls)

        # return HttpResponse(json.dumps({'image_urls': image_urls}), content_type="application/json")

        if not selected_platforms:  # If no platforms are selected
            messages.error(request, 'Please select at least one platform.')

        if "Facebook_box" in selected_platforms:
            post_to_facebook(message, image_bytes_list)

        if "Twitter_box" in selected_platforms:
            post_to_twitter(message, image_path_list)

        if "Instagram_box" in selected_platforms:            
            post_to_instagram(message, image_urls)
        
    # Remember to stop ngrok and the HTTP server when you're done
    ngrok.terminate()
    httpd.shutdown()

# Redirect back to the post page after processing the form submission
    return render(request, 'base_createpost.html')


def post_to_twitter(message, image_path):

    client_v1 = tweepy.OAuth1UserHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET_KEY)
    client_v1.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    client_v1_api = tweepy.API(client_v1)

    client_v2 = tweepy.Client(
        consumer_key=TWITTER_CONSUMER_KEY, consumer_secret=TWITTER_CONSUMER_SECRET_KEY,
        access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)
    
    # get media_id of upload images
    media_id_list = []
    for image in image_path:
        media_id = client_v1_api.media_upload(image).media_id_string
        media_id_list.append(media_id)
        print(media_id)
    print(media_id_list)

# original
# def post_to_twitter(message, image_path):
#     client = tweepy.Client(
#         consumer_key=TWITTER_CONSUMER_KEY, consumer_secret=TWITTER_CONSUMER_SECRET_KEY,
#         access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)
    
#     media_id_list = []
#     image_api_url = 
#     for image in image_path:
#         # Upload the image
#         media_id = client.
#         media_id_list.appe(media_id)

#     response = client.create_tweet(text = message, media_ids=image_path)

#     if response.errors:
#         print("Failed to post to Twitter:", response.errors)
#     else:
#         print("Posted to Twitter successfully")

#     return redirect('post_page')


# def post_to_twitter(message, image_path):
#     auth = tweepy.OAuth1UserHandler(
#         TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET_KEY,
#         TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

#     # Authenticate using OAuth1
#     api = tweepy.API(auth)

#     media_id_list = []
#     for image in image_path:
#         # Upload the image
#         media_id = api.media_upload(image).media_id_string
#         media_id_list.appe(media_id)
#         print(media_id)

#     # Create the tweet with the uploaded media ID
#     response = api.update_status(status=message, media_ids=media_id_list)
#     if response.errors:
#         print("Failed to post to Twitter:", response.errors)
#     else:
#         print("Posted to Twitter successfully")

#     return redirect('post/createpost/')


def create_text_image(text):
    max_width = 1080
    max_height = 1080
    font_size = 75
    line_height = 90
    font_path = "arial.ttf"
    background_color = 'white'
    text_color = 'black'

    # Create a blank image with white background
    img = Image.new('RGBA', (max_width, max_height), background_color)
    # Load a font
    font = ImageFont.truetype(font_path, font_size)
    # Wrap the text to fit within the maximum width
    # wrapped_text = textwrap.fill(text, width=50)
    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Function to calculate text size
    def get_text_size(font, text):
        return draw.textsize(text, font=font)
    
    # Calculate initial text size
    text_width, text_height = get_text_size(font, text)

    # Reduce font size until text fits within the image boundaries
    while text_width > max_width or text_height > max_height:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = get_text_size(font, text)

    # Draw the text on the image
    y_position = (max_height - text_height) // 2
    for line in text.split('\n'):
        line = line.strip()  # Remove leading and trailing whitespace
        line_width, _ = get_text_size(font, line)
        x_position = (max_width - line_width) // 2
        draw.text((x_position, y_position), line, font=font, fill=text_color)
        y_position += line_height  # Increase y position for the next line

    # Generate file name with current date and time
    current_datetime = datetime.now().strftime("%Y%m%d%H%M")
    file_name = f"instagram_{current_datetime}.png"
    target_path = os.path.join(IMAGE_PATH, 'instagram_images', file_name)
    img.save(target_path)
    return target_path


def post_page(request):
    return render(request,'post.html')

