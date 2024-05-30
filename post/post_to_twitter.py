from django.conf import settings

import tweepy as tweepy



TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET_KEY = settings.TWITTER_CONSUMER_SECRET_KEY
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

# twitter v1 method to uplaod images and get media_id
# twitter v2 method to upload post with v1_media_id

def post_to_twitter(message, image_paths):
    client_v1 = get_twitter_conn_v1(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    client_v2 = get_twitter_conn_v2(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)


    media_id_list = []
    for image_instance in image_paths:
    # Get the file path from the image instance
        image_path = image_instance.image.path
        media = client_v1.media_upload(filename=image_path)
        media_id = media.media_id
        media_id_list.append(media.media_id_string)

    try:
        if len(media_id_list) ==0:
            client_v2.create_tweet(text=message)
        else:
            client_v2.create_tweet(text=message, media_ids=media_id_list)
        print("Posted to X(Twitter) successfully")
    except:
        print("Failed to posted to X(Twitter)")



def get_twitter_conn_v1(api_key, api_secret, access_token, access_token_secret) -> tweepy.API:
    """Get twitter conn 1.1"""

    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(access_token,access_token_secret)
    return tweepy.API(auth)

def get_twitter_conn_v2(api_key, api_secret, access_token, access_token_secret) -> tweepy.Client:
    """Get twitter conn 2.0"""

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    return client
