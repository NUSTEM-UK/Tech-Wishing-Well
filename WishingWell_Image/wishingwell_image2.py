#!/usr/bin/env python

# Image processing for Technology Wishing Well system/
# Let's see what this new capture_continuous class camera can do.
# Based on forum code by OutoftheBOTS:
# https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=194059&sid=c31bbc7bbc9276a185b4498da04acf52#p1215709

import io, time, sys
import pygame

import picamera
import picamera.array
# from picamera import PiCamera
# from picamera.array import PiRGBArray
from PIL import Image, ImageStat, ImageOps, ImageDraw
import numpy as np
import os.path
from sys import argv

script, file_prefix = argv

# Set working frame size. Stick with multiples of 32:
# eg. 736, 800, 864, 896, 960, 1024, 1056.
# A good compromise for a 1080-line HD display is 854 px square.
size = width, height = 736, 736

# Set up some configuration variables
full_screen = 1
video_framerate = 15
# Output directory and frequency (how many frames before between outputs?)
output_directory = "/home/pi/outputs"
framedump_interval = 1000
# Default image processing settings
threshold_low = 120
threshold_high = 160

shutter_max = (1.0/video_framerate) * 1000000  # microsec exposure for shutter setting
shutter_min = 1000              			   # microsec exposure for shutter setting
video_rotation = 180
video_port = True
video_stabilization = False
video_annotate_background = False
video_annotate_frame_num = False

frame_count = 1

# Initialise PyGame surface
pygame.init()
if full_screen:
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    pygame.mouse.set_visible(0)
else:
    screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
pygame.display.flip()

# Initialise PIL image to black background
composite = Image.frombytes('RGB', size, "\x00" * width * height * 3)
composite = composite.convert('RGBA')
raw_str = composite.tostring("raw", 'RGBA')
pygame.surface = pygame.image.fromstring(raw_str, size, 'RGBA')

# Set up overlay mask image
# Oversize so it anti-aliases on scaledown
overmask_size = (width * 3, height * 3)
overmask_centre = [ overmask_size[0] / 2 , overmask_size[1] / 2 ]
overmask_radius = overmask_size[0] / 2

# Import the helper functions.
# This may not work because somet things aren't defined yet.
from ww_image_functions import drawOvermask, get_brightness, framedump, handlePygameEvents


# Fire up the camera!
camera = picamera.PiCamera()
camera.resolution = (width, height)
camera.framerate = 15
camera.video_stabilization = video_stabilization

# run the camera to set exposure values
camera.iso = 100
camera.start_preview()
# Wait for automatic gain control to settle
time.sleep( int(20/video_framerate) )
# Now fix the values
camera.shutter_speed = camera.exposure_speed
brightness = camera.brightness
camera.exposure_mode = 'off'
white_balance = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = white_balance
camera.stop_preview()

# Output camera parameters for debugging purposes
print "Shutter speed %s" % camera.shutter_speed
print "White Balance (red, blue): %s" % (white_balance,) # comma is weird tuple munging thing
print "Camera Brightness: %s" % brightness

# Set up mask image
drawOvermask()

# Note that array size arguments are the other way around to the camera resolution. Just to catch you out.
rawCapture = picamera.PiRGBArray(camera, size=(height, width))
time.sleep(0.1)

time_begin = time.time()
time_start = time.time()
frame_count = 1

# Work through the stream of images from the camera
for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    frame_new = frame.array  # the frame will be stored in the variable called image
    # BEGIN Image processing code 
    
    # Create YUV conversion for luminosity mask processing
    frame_yuv = frame_new.convert("YCbCr")
    frame_yuv_array = np.array(frame_yuv)
    frame_y = frame_yuv_array[0:width, 0:height, 0]

    # ***** MASK PROCESSING *****
    # Clip low values to black (transparent)
    # First index the low values...
    low_clip_indices = frame_y < threshold_low
    # ...then set values at those indices to zero
    frame_y[low_clip_indices] = 0

    # Clip high values to white (solid)
    # First index the high values...
    high_clip_indices = frame_y > threshold_high
    # ...then set values at those indices to 255
    frame_y[high_clip_indices] = 255
    
    # Make mask image from Numpy array frame_y
    mask = Image.fromarray(frame_y, "L")
    # mask.save("mask-after.jpeg")

    # ***** COMPOSITE NEW FRAME *****
    # Convert captured frame to RGBA
    frame_new = frame_new.convert("RGBA")
    
    # Combine captured frame with rolling composite, via computed mask
    # TODO: Check this is really doing what we think it is
    composite.paste(frame_new, (0,0), mask)
    
    # Apply overlay mask
    composite.paste(overmask, (0,0), ImageOps.invert(overmask))
    
    # ***** DISPLAY NEW FRAME *****    
    raw_str = composite.tostring("raw", 'RGBA')
    pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')
    
    # Finally, update the window
    screen.blit(pygame_surface, (0,0))
    pygame.display.flip()

    time_taken = time.time() - time_start
    time_since_begin = time.time() - time_begin
    print "Frame %d in %.3f secs, at %.2f fps: shutter: %d, low: %d high: %d" % (frame_count, time_taken, (frame_count/time_since_begin), camera.shutter_speed, threshold_low, threshold_high)
    
    # Clear the buffer!
    rawCapture.truncate(0)
    time_start = time.time()
    frame_count += 1

    if (frame_count % framedump_interval == 0):
        framedump()