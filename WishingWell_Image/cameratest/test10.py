# Based on forum code by OutoftheBOTS:
# https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=194059&sid=c31bbc7bbc9276a185b4498da04acf52#p1215709

import time

from picamera import PiCamera
from picamera.array import PiRGBArray

camera = PiCamera()
# set capture resolution. Multiples of 16, typically!
width, height = (864, 864)
camera.resolution = (width, height)
# Note that array size arguments are the other way around to the camera resolution. Just to catch you out.
rawCapture = PiRGBArray(camera, size=(height, width))
camera.framerate = 15
time.sleep(0.1)

time_begin = time.time()
time_start = time.time()
frame_count = 0

# through the stream of images from the camera
for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    image = frame.array  # the frame will be stored in the varible called image
    # add your processing code here to process the image array
    time_taken = time.time() - time_start
    time_since_begin = time.time() - time_begin
    print("Frame %d captured in %.3f secs, at %.2f fps" %
          (frame_count, time_taken, (frame_count / time_since_begin)))
    # Clear the buffer!
    rawCapture.truncate(0)
    time_start = time.time()
    frame_count += 1
