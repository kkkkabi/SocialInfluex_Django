from django.shortcuts import render, redirect
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Sum

import requests
import os

from .models import UploadImages, OverviewInsight, PostInsight
from .post_to_instagram import post_to_instagram, create_text_image
from .post_to_facebook import post_to_facebook
from .post_to_twitter import post_to_twitter

import http.server
import socketserver
import threading
import subprocess
import time
import json

IMAGE_PATH = settings.MEDIA_ROOT

# https://facebook-sdk.readthedocs.io/en/latest/api.html

def post_to_selected_platforms(request):
    if request.method == "POST":
        message = request.POST.get('message', '')
        image_files = request.FILES.getlist('uploadFiles')  # Retrieve uploaded images
        selected_platforms = request.POST.getlist('platforms')  # get platforms list

        # Start a simple HTTP server in a new thread
        PORT = 3000
        Handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", PORT), Handler)
        thread = threading.Thread(target=httpd.serve_forever)
        thread.start()

        # Start ngrok
        ngrok = subprocess.Popen(["ngrok", "http", str(PORT)], stdout=subprocess.PIPE)

        # Give ngrok time to start up
        time.sleep(2)

        # Get the public URL from ngrok
        resp = requests.get("http://localhost:4040/api/tunnels")
        public_url = resp.json()["tunnels"][0]["public_url"]
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
        messages.info(request, 'create post successfully')

# Redirect back to the post page after processing the form submission
    return render(request, 'base_createpost.html')


def insight(request):
    platform_insight = OverviewInsight.objects.order_by('platform_id')
    total_page_reach = OverviewInsight.objects.aggregate(total_reach=Sum('no_of_page_reach'))['total_reach']
    total_page_likes = OverviewInsight.objects.aggregate(total_likes=Sum('no_of_page_likes'))['total_likes']
    total_page_followers = OverviewInsight.objects.aggregate(total_followers=Sum('no_of_page_followers'))['total_followers']
    total_page_posts = OverviewInsight.objects.aggregate(total_posts=Sum('no_of_published_post'))['total_posts']

    return render(request,
                  'base_insight.html',
                   {'platform_insight': platform_insight,
                    'total_page_reach':total_page_reach,
                    'total_page_likes':total_page_likes,
                    'total_page_followers':total_page_followers,
                    'total_page_posts':total_page_posts,
                    })