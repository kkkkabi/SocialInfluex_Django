from django.shortcuts import render, redirect
from django.conf import settings
from datetime import datetime
from uuid import uuid4
import tweepy as tweepy
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap

IMAGE_PATH = settings.MEDIA_ROOT

INSTAGRAM_BUSINESS_ACCOUNT_ID = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
INSTAGRAM_PAGE_ACCESS_TOKEN = settings.INSTAGRAM_PAGE_ACCESS_TOKEN
container_url = 'https://graph.facebook.com/v19.0/{}/media'.format(INSTAGRAM_BUSINESS_ACCOUNT_ID)
publish_url = 'https://graph.facebook.com/v19.0/{}/media_publish'.format(INSTAGRAM_BUSINESS_ACCOUNT_ID)


def post_to_instagram(message, image_urls):
    if len(image_urls) == 1:
        return post_to_instagram_single_image(message, image_urls[0])
    
    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = {executor.submit(create_item_container, image_url) for image_url in image_urls}
        # Gather the results as they become available
        children = [future.result() for future in futures if future.result() is not None]

    if children:
        carousel_id = create_carousel_container(children, message)
        if carousel_id:
            return publish_carousel_container(carousel_id)

    return False  # return False if the operation failed

# create post to instagram
def post_to_instagram_single_image(message, image_url):
    container_id = create_item_container_single_image(message, image_url)
    if container_id:
        return create_publish_container_single_image(container_id)
    return False

# post to Instagram with multiple images
#step1
def create_item_container(image_url):
    payload = {
        'image_url': image_url,  
        'is_carousel_item': True,  
        'access_token': INSTAGRAM_PAGE_ACCESS_TOKEN  
    } 
    res = requests.post(container_url, payload)
    if res.status_code != 200:
        print("Failed to create an item container.")
        return None
    else:
        result = res.json()
        print("Item container created successfully:", result['id'])
        return result['id']
    
#step2
def create_carousel_container(children, message):
    payload = {  
        'children': ','.join(children),
        'media_type': 'CAROUSEL',
        'caption': message,
        'access_token': INSTAGRAM_PAGE_ACCESS_TOKEN
    } 
    res = requests.post(container_url, payload)
    if res.status_code != 200:
        print("Failed to create a media container.")
        return None
    else:
        result = res.json()
        carousel_continer_id = result['id']
        print("Create a container successfully:", carousel_continer_id)
        return carousel_continer_id

#step 3
def publish_carousel_container(creation_id):
    payload = {  
        'creation_id': creation_id,
        'access_token': INSTAGRAM_PAGE_ACCESS_TOKEN  
    }
    res = requests.post(publish_url, payload)
    if res.status_code != 200:
        print("Failed to post to Instagram.")
        return None
    else:
        print("Posted to Instagram successfully.")


# post to instagram with single image
#step 1
def create_item_container_single_image(message, image_url):
    payload = {
        'image_url': image_url,
        'caption': message,
        'access_token': INSTAGRAM_PAGE_ACCESS_TOKEN
    }
    res = requests.post(container_url, payload)
    if res.status_code != 200:
        print("Failed to create single item container for image URL", image_url)
        return None
    else:
        print('Single item container created for image URL: %s', image_url)
        result = res.json()
        continer_id = result['id']
        return continer_id
#step2
def create_publish_container_single_image(creation_id):
    payload = {
        'creation_id': creation_id,
        'access_token': INSTAGRAM_PAGE_ACCESS_TOKEN
    }
    res = requests.post(publish_url, payload)
    if res.status_code != 200:
        print("Failed to post to Instagram with single image.")
        return None
    else:
        print('Successfully post to Instagram with single image.')

def create_text_image(text):
    max_width = 1080
    max_height = 1080
    font_size = 75
    line_height = 90
    font_path = "arial.ttf"
    background_color = 'white'
    text_color = 'black'
    file_path = "../../media/Instagram_upload"

    # Create a blank image with white background
    img = Image.new('RGBA', (max_width, max_height), background_color)
    # Load a font
    font = ImageFont.truetype(font_path, font_size)
    # Wrap the text to fit within the maximum width
    wrapped_text = textwrap.fill(text, width=50)
    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Function to calculate text size
    def get_text_size(font, text):
        return draw.textsize(text, font=font)
    
    # Calculate initial text size
    text_width, text_height = get_text_size(font, wrapped_text)

    # Reduce font size until text fits within the image boundaries
    while text_width > max_width or text_height > max_height:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = get_text_size(font, wrapped_text)

    # Draw the text on the image
    y_position = (max_height - text_height) // 2
    for line in wrapped_text.split('\n'):
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

