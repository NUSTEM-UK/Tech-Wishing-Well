#!/usr/bin/env python

# Image processing for Technology Wishing Well system/
# Let's see what this new capture_continuous class camera can do.
# Based on forum code by OutoftheBOTS:
# https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=194059&sid=c31bbc7bbc9276a185b4498da04acf52#p1215709

import io, time, sys
import pygame

import picamera
# import picamera.array
# from picamera import PiCamera
from picamera.array import PiRGBArray, PiYUVArray
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
full_screen = 0
video_framerate = 8
# Output directory and frequency (how many frames before between outputs?)
output_directory = "/home/pi/outputs"
framedump_interval = 1000
# Default image processing settings
threshold_low = 40
threshold_high = 230

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
raw_str = composite.tobytes("raw", 'RGBA')
pygame.surface = pygame.image.fromstring(raw_str, size, 'RGBA')

# Set up overlay mask image
# Oversize so it anti-aliases on scaledown
overmask_size = (width * 3, height * 3)
overmask_centre = [ overmask_size[0] / 2 , overmask_size[1] / 2 ]
overmask_radius = overmask_size[0] / 2

from PIL import Image, ImageStat, ImageOps, ImageDraw
import numpy as np
import os.path

def drawOvermask():
    global overmask
    global overmask_size
    global overmask_radius
    global overmask_centre
    overmask = Image.new('L', overmask_size, 0)
    draw = ImageDraw.Draw(overmask)
    draw.ellipse (  (
        (overmask_centre[0] - overmask_radius),
        (overmask_centre[1] - overmask_radius),
        (overmask_centre[0] + overmask_radius),
        (overmask_centre[1] + overmask_radius) ), fill = 255)
    overmask = overmask.resize(size, Image.ANTIALIAS)


def get_brightness(image):
    """Return overall brightness value for image"""
    stat = ImageStat.Stat(image)
    return stat.rms[0]


def framedump():
    global file_prefix
    global frame_count
    global output_directory
    global composite
    framedump_name = file_prefix + "-frame-" + str(frame_count) + ".jpeg"
    filename = os.path.join(output_directory, framedump_name)
    composite.save(filename)
    print "Frame saved as %s" % framedump_name


def handlePygameEvents():
    global threshold_low
    global threshold_high
    global composite
    global frame_count
    global overmask_size
    global overmask_centre
    global overmask_radius
    global full_screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type is pygame.KEYDOWN:
            key_press = event.key
            # key_press = pygame.key.name(event.key)
            # print key_press # For diagnostic purposes, but messes up output
            if key_press == pygame.K_s:
                if (camera.shutter_speed - 1000) >= shutter_min:
                    camera.shutter_speed -= 1000
                print "Shutter speed set to: %s" % camera.shutter_speed
            elif key_press == pygame.K_w:
                if (camera.shutter_speed + 1000) <= shutter_max:
                    camera.shutter_speed += 1000
                print "Shutter speed set to: %s" % camera.shutter_speed
            elif key_press == pygame.K_e:
                if (threshold_low + 1) < 256:
                    threshold_low += 1
                print "threshold_low set to %i" % threshold_low
            elif key_press == pygame.K_d:
                if (threshold_low - 1) >= 0:
                    threshold_low -= 1
                print "threshold_low set to %i" % threshold_low
            elif key_press == pygame.K_r:
                if (threshold_high + 1) < 256:
                    threshold_high += 1
                print "threshold_high set to %i" % threshold_high
            elif key_press == pygame.K_f:
                if (threshold_high -1) >= 0:
                    threshold_high -= 1
                print "threshold_high set to %i" % threshold_high
            elif key_press == pygame.K_m:
                if full_screen:
                    pygame.display.set_mode(size)
                    pygame.mouse.set_visible(1)
                else:
                    pygame.display.set_mode(size, pygame.FULLSCREEN)
                    pygame.mouse.set_visible(0)
                full_screen = not full_screen
            elif key_press == pygame.K_i:
                if ( overmask_centre[1] - 10 ) > 0:
                    overmask_centre[1] -= 10
                    drawOvermask()
            elif key_press == pygame.K_k:
                if ( overmask_centre[1] + 10 ) < overmask_size[1]:
                    overmask_centre[1] += 10
                    drawOvermask()
            elif key_press == pygame.K_j:
                if ( overmask_centre[0] - 10 ) > 0:
                    overmask_centre[0] -= 10
                    drawOvermask()
            elif key_press == pygame.K_l:
                if ( overmask_centre[0] + 10 ) < overmask_size[0]:
                    overmask_centre[0] += 10
                    drawOvermask()
            elif key_press == pygame.K_y:
                overmask_radius += 10
                drawOvermask()
            elif key_press == pygame.K_h:
                overmask_radius -= 10
                drawOvermask()
            elif key_press == pygame.K_o:
                framedump()
            
            # Check for left shift and allow rapid threshold changes
            if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                if key_press == pygame.K_q:
                    sys.exit()
                if key_press == pygame.K_e:
                    if (threshold_low + 10) < 256:
                        threshold_low += 10
                    print "threshold_low set to %i" % threshold_low
                elif key_press == pygame.K_d:
                    if (threshold_low - 10) >= 0:
                        threshold_low -= 10
                    print "threshold_low set to %i" % threshold_low
                elif key_press == pygame.K_r:
                    if (threshold_high + 10) < 256:
                        threshold_high += 10
                    print "threshold_high set to %i" % threshold_high
                elif key_press == pygame.K_f:
                    if (threshold_high -10) >= 0:
                        threshold_high -= 10
                    print "threshold_high set to %i" % threshold_high
                elif key_press == pygame.K_s:
                    if (camera.shutter_speed - 10000) >= shutter_min:
                        camera.shutter_speed -= 10000
                    print "Shutter speed set to: %s" % camera.shutter_speed
                elif key_press == pygame.K_w:
                    if (camera.shutter_speed + 10000) <= shutter_max:
                        camera.shutter_speed += 10000
                    print "Shutter speed set to: %s" % camera.shutter_speed
                # Check for SHIFT+P and if found, set working image to pure black again
                elif key_press == pygame.K_p:
                    print "*** STARTING OVER ***"
                    composite = Image.frombytes('RGB', size, "\x00" * width * height * 3)
                    composite = composite.convert('RGBA')

# So... that code happened.
# TODO Refactor this mess

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
rawCapture = PiRGBArray(camera, size=(height, width))
#rawCapture = PiYUVArray(camera, size=(height, width))
time.sleep(0.1)

time_begin = time.time()
time_start = time.time()
frame_count = 1

# Set up a conversion matrix to YUV from RGB
yuv_from_rgb = np.array([[ 0.299 , 0.587 , 0.114],
                         [ -0.14714119, -0.28886916, 0.43601035 ],
                         [ 0.61497538, -0.51496512, -0.10001026 ]])

# Work through the stream of images from the camera
for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    
    # frame_new = Image.frombytes('RGB', size, frame.array)
    # frame_yuv = Image.frombytes('yuv', size, frame.array)
    frame_rgb_array = frame.array
    frame_rgb_image = Image.fromarray(frame_rgb_array)

    # BEGIN Image processing code 
    
    # Create YUV conversion for luminosity mask processing
    frame_yuv_array = frame_rgb_array.dot(yuv_from_rgb.T.copy())
    #frame_yuv = frame_rgb_image.convert("YCbCr")
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
    frame_rgb_image = frame_rgb_image.convert("RGBA")
    
    # Combine captured frame with rolling composite, via computed mask
    # TODO: Check this is really doing what we think it is
    composite.paste(frame_rgb_image, (0,0), mask)
    
    # Apply overlay mask
    composite.paste(overmask, (0,0), ImageOps.invert(overmask))
    
    # ***** DISPLAY NEW FRAME *****    
    raw_str = composite.tobytes("raw", 'RGBA')
    pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')
    
    # Finally, update the window
    screen.blit(pygame_surface, (0,0))
    pygame.display.flip()

    # Handle PyGame events (ie. keypress controls)
    handlePygameEvents()

    time_taken = time.time() - time_start
    time_since_begin = time.time() - time_begin
    print "Frame %d in %.3f secs, at %.2f fps: shutter: %d, low: %d high: %d" % (frame_count, time_taken, (frame_count/time_since_begin), camera.shutter_speed, threshold_low, threshold_high)
    
    # Clear the buffer!
    rawCapture.truncate(0)
    time_start = time.time()
    frame_count += 1

    if (frame_count % framedump_interval == 0):
        framedump()