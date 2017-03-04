#!/usr/bin/env python3
""" This script allows the user to take a photo and to upload load it with a
user-selected tweet."""
import time
import glob
import os
import random
from stat import ST_MTIME
from gpiozero import LED, Button
from twython import Twython, TwythonError
import picamera
from random_proverbs import proverbList



# define the pins for the buttons
snapButton = Button(24,bounce_time=1)
selectButton= Button(23,bounce_time=1)

# define the pins for the LEDs
topLED=LED(13)
middleLED=LED(5)
bottomLED =LED(6)

# config the Twitter API client
config= {}
execfile("realconfig.py", config)
twitter = Twython(config["app_key"], config["app_secret"], config["oauth_token"], config["oauth_token_secret"])

# config the camera
camera= picamera.PiCamera()
camera.led= False
camera.resolution= (1360, 768)
camera.start_preview()

def LEDconfig(whichlight):
    if whichlight == 1:
        topLED.on()
        middleLED.off()
        bottomLED.off()
        tweet = "Having a blast at the #piparty birthday bash 2017!"
        return tweet
    elif whichlight == 2:
        topLED.off()
        middleLED.on()
        bottomLED.off()
        tweet = "Looking forward to @makerfaire_uk 2017 on the 1st and 2nd April in Newcastle!"
        return tweet
    else:
        topLED.off()
        middleLED.off()
        bottomLED.on()
        tweet = "random"
        return tweet

def flasher():
    for i in range(3):
        topLED.on()
        bottomLED.on()
        middleLED.on()
        time.sleep(0.2)
        topLED.off()
        bottomLED.off()
        middleLED.off()
        time.sleep(0.2)


def tww_image_getter(nf_timestamp):
    try:
        files = glob.glob('/home/pi/Maker_Faire_2016/Outputs/*.jpeg')
        for name in files:
            st = os.stat(name)
            if st[ST_MTIME] > nf_timestamp:
                nf_timestamp= st[ST_MTIME]
                photo= open(name, 'rb')
                response= twitter.upload_media(media= photo)
                twitter.update_status(status = "Behold the beauty of the Tech Wishing Well. Thanks for all your contributions so far!", media_ids=[response['media_id']])
                photo.close()
                return nf_timestamp
    except:
        pass

def take_photo():
    camera.led = True
    camera.annotate_text = '3'
    time.sleep(0.7)
    camera.annotate_text = '2'
    time.sleep(0.7)
    camera.annotate_text = '1'
    time.sleep(0.7)
    camera.annotate_text = 'Smile!'
    time.sleep(0.1)
    camera.annotate_text = ''
    camera.led = False

    print("Taking photo")
    camera.capture("picamimg.jpg")
    print("Photo done!")

def twitter_upload(message, filep):
    if message == "random":
        message = proverbList[random.randint(0,len(proverbList))-1] + ". Wow this Tech Wishing Well is deep!"
    photo = open(filep, 'rb')
    response = twitter.upload_media(media = photo)
    print("Uploading tweet...")
    try:
        twitter.update_status(status = message, media_ids=[response['media_id']])
        print("Upload successful")
    except TwythonError as e:
        print(e.error_code)



def main():
    # initial message and light config
    topLED.on()
    middleLED.off()
    bottomLED.off()
    message = "Having a blast at the #PiParty birthday bash 2017!"
    location = 1
    newfile_timestamp = 0

    try:
        while True:
            newfile_timestamp = tww_image_getter(newfile_timestamp)
            if snapButton.is_pressed:
                print("Snap...")
                take_photo()
                flasher()
                twitter_upload(message, "picamimg.jpg")
                LEDconfig(location)

            elif selectButton.is_pressed:
                print("Change selection...")
                time.sleep(0.2)
                if location == 1:
                    message = LEDconfig(1)
                    print(message)
                    location = 2
                elif location == 2:
                    message = LEDconfig(2)
                    print(message)
                    location = 3
                else:
                    message = LEDconfig(3)
                    print(message)
                    location = 1
    finally:
        camera.stop_preview()

if __name__ == '__main__':
    main()
