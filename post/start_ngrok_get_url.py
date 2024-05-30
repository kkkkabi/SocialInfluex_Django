import requests
import http.server
import socketserver
import threading
import subprocess
import time
import json
import os

from .models import UploadImages
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from django.conf import settings

IMAGE_PATH = settings.MEDIA_ROOT
# Function to start ngrok and return its process
def start_ngrok(port):
    ngrok_process = subprocess.Popen(["ngrok", "http", str(port)], stdout=subprocess.PIPE)
    time.sleep(2)  # Wait for ngrok to initialize
    return ngrok_process

# Function to stop ngrok
def stop_ngrok(ngrok_process):
    ngrok_process.terminate()

# Function to start the HTTP server
def start_http_server(port):
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()
    return httpd

# Function to stop the HTTP server
def stop_http_server(httpd):
    httpd.shutdown()

# Function to get the ngrok public URL
def get_ngrok_public_url():
    try:
        resp = requests.get("http://localhost:4040/api/tunnels")
        resp.raise_for_status()  # Raise an exception for non-200 status codes
        public_url = resp.json()["tunnels"][0]["public_url"]
        return public_url
    except (requests.RequestException, KeyError, IndexError) as e:
        # Handle errors gracefully
        print("Error getting ngrok public URL:", e)
        return None

def create_text_image_and_get_image_url(text):
    # Create text image
    image_path = create_text_image(text)
    # Upload image and get URL
    public_url = get_ngrok_public_url()
    if public_url:
        file_name = os.path.basename(image_path)
        img_url = f"{public_url}/media/instagram_images/{file_name}"
        return [img_url]
    else:
        return []
    
# Function to upload images and get URLs
def upload_images_and_get_image_url(image_files):
    # Start ngrok and HTTP server
    port = 8080
    ngrok_process = start_ngrok(port)
    httpd = start_http_server(port)

    # Get ngrok public URL
    public_url = get_ngrok_public_url()
    if not public_url:
        # Handle failure to get ngrok public URL
        stop_ngrok(ngrok_process)
        stop_http_server(httpd)
        return []

    # Upload images and get URLs
    image_url_list = []
    for image in image_files:
        image_instance = UploadImages.objects.create(image=image)
        image_instance.save()
        file_name = os.path.basename(image_instance.image.name)
        img_url = f"{public_url}/media/post_images/{file_name}"
        image_url_list.append(img_url)

    # Stop ngrok and HTTP server
    stop_ngrok(ngrok_process)
    stop_http_server(httpd)

    return image_url_list



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