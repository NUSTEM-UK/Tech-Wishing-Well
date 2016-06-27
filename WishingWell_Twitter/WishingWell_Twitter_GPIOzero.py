# Import the necessary module: GPIO, Twython, Time and PiCamera
from gpiozero import Button, LED
import os, time, sys, random
from twython import Twython
import picamera
from datetime import datetime
from random_proverbs import *
#from  random_scientists import *
from generic_tweets import *

# these modules allow us to import data on the image files to be tweeted on the hour
from stat import *
import glob

# set integers for the various buttons and LEDs
select_btn = Button(17)
tweet_btn = Button(27)
reset_btn = Button(21)
t_LED = LED(22)
m_LED = LED(23)
b_LED = LED(24)

# open and load the config file for the Twitter client (Twython)
config = {}
execfile("real_config.py", config)
twitter = Twython(config["app_key"],config["app_secret"],config["oauth_token"],config["oauth_token_secret"])

## get the time stamp of the most recent jpeg in the output folder
#files = glob.glob('/home/pi/Maker_Faire_2016/Outputs/*.jpeg')
#newfile_timestamp = 0
#newest_file = ""

## datetime setup to add string to an image file
FORMAT = '%Y%m%d%H%M%S'


#for name in files:
    #st = os.stat(name)
    #if st[ST_MTIME] > newfile_timestamp:
            #newfile_timestamp = st[ST_MTIME]
            #newest_file = name
            
#print "The most recent file is:" + newest_file    
#print "Created at timestamp:" + str(newfile_timestamp)  

# set the choice fucntion to 0 [it can have values 0,1,2]
tweet_choice = 0
t_LED.on()
m_LED.off()
b_LED.off()

# this is the button debounce function
def debounce():
    time.sleep(0.4)

# the three Tweets (to rule them all)
tweet0 = ""
tweet1 = ""
tweet2 = ""
wishing_well_tweet = "Come and cast your wish at the @thinkphysicsne Tech Wishing Well #bigbangne"

#create and rotate the PiCamera
camera = picamera.PiCamera()
camera.led = False
camera.rotation = 270
camera.start_preview()


try:
    while True:
        #files = glob.glob('/home/pi/Maker_Faire_2016/Outputs/*.jpeg')
        #for name in files:
            #st = os.stat(name)
            #if st[ST_MTIME] > newfile_timestamp:
                #newfile_timestamp = st[ST_MTIME]
                #newest_file = name
                #photo = open(newest_file, 'rb')
                #response = twitter.upload_media(media = photo)
                #twitter.update_status(status = wishing_well_tweet, media_ids=[response['media_id']])
                #photo.close()
        if select_btn.is_pressed:
            print("Select Pressed")
            if tweet_choice == 0:
                tweet_choice = 1
                print(tweet_choice)
                t_LED.off()
                m_LED.on()
                b_LED.off()
            elif tweet_choice == 1:
                tweet_choice = 2
                print(tweet_choice)
                t_LED.off()
                m_LED.off()
                b_LED.on()                
            else:
                tweet_choice = 0
                print(tweet_choice)
                t_LED.on()
                m_LED.off()
                b_LED.off()
            debounce()
        elif tweet_btn.is_pressed:
            print("Select Pressed")
            camera.led = True
            if tweet_choice == 0:
                twit_message = proverbList[random.randint(0,len(proverbList))-1] + " #bigbangne"
            elif tweet_choice == 1:
                twit_message = genericList[random.randint(0,len(genericList))-1]
            else:
                twit_message = proverbList[random.randint(0,len(proverbList))-1] + " I'm at #bigbangne with my tech wish for the future!" 
            
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
            image_path = "/home/pi/Maker_Faire_2016/TwitterImages/%s-image.jpg" % datetime.now().strftime(FORMAT)
            camera.led = False
            camera.resolution = (1360, 768)
            camera.capture(image_path)
            photo = open(image_path, 'rb')
            response = twitter.upload_media(media = photo)
            twitter.update_status(status = twit_message, media_ids=[response['media_id']])
            debounce()
        elif reset_btn.is_pressed:
			print("Fail")
			sys.exit()

finally:
    print("Oh dear")
    # cleanup the GPIO pins on keyboard interupt
    #GPIO.cleanup()
    # stop the camera preview on keyboard interupt
    camera.stop_preview()

     

