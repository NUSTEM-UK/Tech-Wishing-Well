from gpiozero import LED, Button
import time
import sys
import random
from twython import twython
import picamera
from datetime import datetime
from random_proverbs import *
from random_scientists import *
from generic_tweets import *

# define the pins for the buttons
snapButton = Button(23)
selectButton = Button(24)

# define the pins for the LEDs
topLED = LED(5)
middleLED = LED(6)
bottomLED = LED(13)

# initial message and light config
topLED.on()
middleLED.off()
bottomLED.off()
message = "Having a blast @raspberrypi birthday bash 2017!"
location = 1

# config the Twitter API client
config={}
execfile("realconfig.py", config)
twitter = Twython(config["app_key"],config["app_secret"],config["oauth_token"],config["oauth_token_secret"])

# config the camera
camera = picamera.PiCamera()
camera.led=False
camera.rotation = 270
camera.start_preview()

def take_photo():
    camera.led = True
    time.sleep(1)
    camera.annotate_text = '3'
    time.sleep(1)
    camera.annotate_text = '2'
    time.sleep(1)
    camera.annotate_text = '1'
    time.sleep(1)
    camera.annotate_text = 'Smile!'
    time.sleep(0.7)
    camera.annotate_text = ''
    image_path = "picamimg.jpg"
    camera.led = False
    camera.resolution = (1360, 768)
    camera.capture(image_path)

def twitter_upload(message, file):
    photo = open(image_path, 'rb')
    response = twitter.upload_media(media = photo)
    twitter.update_status(status = message, media_ids=[response['media_id']])

def LEDconfig(location):
    if location == 1:
        topLED.on()
        middleLED.off()
        bottomLED.off()
        message = "Having a blast @raspberrypi birthday bash 2017!"
        return message
    elif location == 2:
        topLED.off()
        middleLED.on()
        bottomLED.off()
        message = "Looking forward to @makerfaireuk 2017 on the 1st and 2nd April in Newcastle!"
        return message
    else:
        topLED.off()
        middleLED.off()
        bottomLED.on()
        message = "Wow these people from @nustemuk are cool!"
        return message
try:
    while True:
        if snapButton.is_pressed:
            take_photo()
            twitter_upload()
            
        elif selectButton.is_pressed:
            if location == 1:
                message = LEDconfig(1)
                location = 2
            elif location == 2:
                message = LEDconfig(2)
                location = 3
            else:
                message = LEDconfig(3)
                location = 1

finally:
    camera.stop_preview()
