from twython import Twython

config = {}
execfile("real_config.py", config)
twitter = Twython(config["app_key"],config["app_secret"],config["oauth_token"],config["oauth_token_secret"])

photo = open('image.jpg', 'rb')
response = twitter.upload_media(media = photo)
twitter.update_status(status = "Testing", media_ids=[response['media_id']])
