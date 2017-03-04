from gpiozero import LED, Button
import time
import random
from twython import Twython, TwythonError
import picamera
from random_proverbs import proverbList

try:
    from stat import *
    import glob
    files = glob.glob('/home/pi/Maker_Faire_2016/Outputs/*.jpeg')
    newfile_timestamp = 0
    newest_file = ""
except:
    pass

# define the pins for the buttons
snapButton = Button(24, bounce_time = 1)
selectButton = Button(23, bounce_time = 1)

# define the pins for the LEDs
topLED = LED(13)
middleLED = LED(5)
bottomLED = LED(6)

# initial message and light config
topLED.on()
middleLED.off()
bottomLED.off()
message = "Having a blast @raspberry_pi birthday bash 2017!"
location = 1

# config the Twitter API client
config={}
execfile("realconfig.py", config)
print(config["app_key"])
twitter = Twython(config["app_key"],config["app_secret"],config["oauth_token"],config["oauth_token_secret"])

# config the camera
camera = picamera.PiCamera()
camera.led=False
camera.start_preview()

def tww_image_getter():
    try:
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
    camera.resolution = (1360, 768)
    print("Taking photo")
    camera.capture("picamimg.jpg")

def twitter_upload(message, filep):
    if message == "random":
        message = proverbList[random.randint(0,len(proverbList))-1] + ". Wow this Tech Wishing Well is deep!"
    photo = open(filep, 'rb')
    response = twitter.upload_media(media = photo)
    print("Uploading tweet")
    try:
        twitter.update_status(status = message, media_ids=[response['media_id']])
        print("Done uploading")
    except TwythonError as e:
        print(e.error_code)

def LEDconfig(location):
    if location == 1:
        topLED.on()
        middleLED.off()
        bottomLED.off()
        message = "Having a blast @raspberry_pi birthday bash 2017!"
        return message
    elif location == 2:
        topLED.off()
        middleLED.on()
        bottomLED.off()
        message = "Looking forward to @makerfaire_uk 2017 on the 1st and 2nd April in Newcastle!"
        return message
    else:
        topLED.off()
        middleLED.off()
        bottomLED.on()
        message = "random"
        return message
try:
    while True:
        tww_image_getter()
        if snapButton.is_pressed:
            print("Pressed 1")
            take_photo()
            twitter_upload(message, "picamimg.jpg")

        elif selectButton.is_pressed:
            print("Pressed 2")
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
