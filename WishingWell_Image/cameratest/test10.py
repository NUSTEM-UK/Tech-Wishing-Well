# Based on forum code by OutoftheBOTS:
# https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=194059&sid=c31bbc7bbc9276a185b4498da04acf52#p1215709

import time
from picamera.array import PiRGBArray
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640, 360)
rawCapture = PiRGBArray(camera, size=(640, 360))
time.sleep(0.1)

START = time()
#cycle through the stream of images from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array #the frame will be stroed in the varible called image
	#add your processing code here to process the image array
    elapsed = time() - start
    print(elapsed)
