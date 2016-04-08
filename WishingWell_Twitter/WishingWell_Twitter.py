# Import the necessary module: GPIO, Twython, Tim and PiCamera
import RPi.GPIO as GPIO
import time
from twython import Twython
import picamera

# create PiCamera
camera = picamera.PiCamera()

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


# this is the button debounce function
def debounce():
    time.sleep(0.4)
    
# this is the fucntion that allows lights to be turned on or off in combo 
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

# write any twitter handles we want to include here
twit_message = "test"
handle1 = "@llewmihs"
handle2 = ""
handle3 = ""

try:
    while True:
        if GPIO.input(select_btn) == False:
            print "The %s has been pressed" % select_btn
            if tweet_choice == 0:
                tweet_choice = 1
                twit_message = tweet1 + " @llewmihs"
                light_switch(False, True, False)
                print "New tweet choice: %s" % tweet1
            elif tweet_choice == 1:
                tweet_choice = 2
                light_switch(False, False, True)
                twit_message = tweet2 + " @llewmihs"
                print "New tweet choice: %s" % tweet2
            else:
                tweet_choice = 0
                light_switch(True, False, False)
                twit_message = tweet0 + " @llewmihs"
                print "New tweet choice: %s" % tweet0
            debounce()
        # this is the if statment that takes the image to upload to twitter
        elif GPIO.input(tweet_btn) == False:
            print "Preparing to take a photo"
            camera.start_preview()
            time.sleep(3)
            camera.rotation = 270
            camera.capture('image.jpg')
            camera.stop_preview()
            # create the tweet
            
            print "Preparing to Tweet the image and message"
            photo = open('image.jpg', 'rb')
            response = twitter.upload_media(media = photo)
            twitter.update_status(status = twit_message, media_ids=[response['media_id']])
            print "Tweet sent successfully"
            debounce()
            
finally:
    GPIO.cleanup()
