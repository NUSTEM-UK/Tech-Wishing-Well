from gpiozero import LED, Button
import random
import time
from twython import Twython
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
message = "Having a blast @raspberry_pi birthday bash 2017!"
location = 1

# config the Twitter API client
config={}
execfile("realconfig.py", config)
twitter = Twython(config["app_key"],config["app_secret"],config["oauth_token"],config["oauth_token_secret"])

# config the camera
camera = picamera.PiCamera()
camera.led=False
camera.rotation = 270
camera.resolution = (1360, 768)
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
    time.sleep(0.7)
    camera.annotate_text = '3'
    time.sleep(0.7)
    camera.annotate_text = '2'
    time.sleep(0.7)
    camera.annotate_text = '1'
    time.sleep(0.7)
    camera.annotate_text = 'Smile!'
    time.sleep(0.4)
    camera.annotate_text = ''
    camera.led = False
    camera.capture("picamimg.jpg")

def twitter_upload(message, path):
    if message == "random":
        message = proverbList[random.randint(0,len(proverbList))-1] + " Wow this Tech Wishing Well is deep!"
    photo = open(path, 'rb')
    response = twitter.upload_media(media = photo)
    try:
        twitter.update_status(status = message, media_ids=[response['media_id']])
    except:
        print("Upload failed")

def LEDconfig(location):
    if location == 1:
        topLED.on()
        middleLED.off()
        bottomLED.off()
        message = "Having a blast @raspberry_pi birthday bash 2017! Here's my tech wish for the future..."
        return message
    elif location == 2:
        topLED.off()
        middleLED.on()
        bottomLED.off()
        message = "Looking forward to @makerfaireuk on the 1st and 2nd April in Newcastle! Here's my tech wish for the future..."
        return message
    else:
        topLED.off()
        middleLED.off()
        bottomLED.on()
        message = "random"
        #message = "Wow these people from @nustemuk are cool! Here's my tech wish for the future..."
        return message

def main():
    try:
        while True:
            if snapButton.is_pressed:
                take_photo()
                twitter_upload(message, "picamimg.jpg")

            elif selectButton.is_pressed:
                time.sleep(0.2)
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

if __name__ == "__main__":
    main()
