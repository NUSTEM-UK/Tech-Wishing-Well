# Import the necessary module: GPIO, Twython, Tim and PiCamera
import RPi.GPIO as GPIO
import os, time, sys
from twython import Twython
import picamera
from datetime import datetime

# these modules allow us to import data on the image files to be tweeted on the hour
from stat import *
import glob

# set integers for the various buttons and LEDs
select_btn = 17
tweet_btn = 27
t_LED = 22
m_LED = 23
b_LED = 24

# set the inputs and outputs from the PiGPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(select_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(tweet_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(t_LED, GPIO.OUT)
GPIO.setup(m_LED, GPIO.OUT)
GPIO.setup(b_LED, GPIO.OUT)

# open and load the config file for the Twitter client (Twython)
config = {}
execfile("real_config.py", config)
twitter = Twython(config["app_key"],config["app_secret"],config["oauth_token"],config["oauth_token_secret"])

# get the time stamp of the most recent jpeg in the output folder
files = glob.glob('/home/pi/Maker_Faire_2016/Outputs/*.jpeg')
newfile_timestamp = 0
newest_file = ""
#print files

# datetime setup to add string to an image file
FORMAT = '%Y%m%d%H%M%S'


for name in files:
    st = os.stat(name)
    if st[ST_MTIME] > newfile_timestamp:
            newfile_timestamp = st[ST_MTIME]
            newest_file = name
            
print "The most recent file is:" + newest_file    
print "Created at timestamp:" + str(newfile_timestamp)       


# this is the button debounce function
def debounce():
    time.sleep(0.4)
    
# this is the function that allows lights to be turned on or off in combo 
def light_switch(top, middle, bottom):
    GPIO.output(t_LED, top)
    GPIO.output(m_LED, middle)
    GPIO.output(b_LED, bottom)
    
# set the choice fucntion to 0 [it can have values 0,1,2]
tweet_choice = 0
light_switch(True, False, False)

# the three Tweets (to rule them all)
tweet0 = "This is the first Tweet"
tweet1 = "This is the second Tweet"
tweet2 = "This is the third Tweet"
wishing_well_tweet = ""

# write any twitter handles we want to include here
twit_message = tweet0

#create and rotate the PiCamera
camera = picamera.PiCamera()
camera.rotation = 270
camera.start_preview()


try:
    while True:
        
        files = glob.glob('/home/pi/Maker_Faire_2016/Outputs/*.jpeg')
        for name in files:
            st = os.stat(name)
            if st[ST_MTIME] > newfile_timestamp:
                newfile_timestamp = st[ST_MTIME]
                newest_file = name
                photo = open(newest_file, 'rb')
                response = twitter.upload_media(media = photo)
                twitter.update_status(status = wishing_well_tweet, media_ids=[response['media_id']])
                photo.close()
        
            
        if GPIO.input(select_btn) == False:
            if tweet_choice == 0:
                tweet_choice = 1
                twit_message = tweet1
                light_switch(False, True, False)
            elif tweet_choice == 1:
                tweet_choice = 2
                light_switch(False, False, True)
                twit_message = tweet2
            else:
                tweet_choice = 0
                light_switch(True, False, False)
                twit_message = tweet0
            debounce()
            
        # this is the if statement that takes the image to upload to twitter
        if GPIO.input(tweet_btn) == False:
            camera.start_preview()
            time.sleep(1)
            camera.annotate_text = '3'
            time.sleep(1)
            camera.annotate_text = '2'
            time.sleep(1)
            camera.annotate_text = '1'
            time.sleep(1)
            camera.annotate_text = 'Smile!'
            time.sleep(0.7)
            image_path = "/home/pi/Maker_Faire_2016/TwitterImages/%s-image.jpg" % datetime.now().strftime(FORMAT)
            camera.capture(image_path)
            camera.annotate_text = ''
            photo = open(image_path, 'rb')
            response = twitter.upload_media(media = photo)
            twitter.update_status(status = twit_message, media_ids=[response['media_id']])
            
            debounce()
        elif GPIO.input(tweet_btn) == False and GPIO.input(select_btn) == False:
            GPIO.cleanup()
            camera.stop_preview()
            sys.exit()
finally:
    # cleanup the GPIO pins on keyboard interupt
    GPIO.cleanup()
    # stop the camera preview on keyboard interupt
    camera.stop_preview()

