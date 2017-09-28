#!/usr/bin/env python

# Image processing using CircularIO capture.
# Gets us to 3fps at 736x736 resolution, with 6fps capture selected.
# Profiling suggests peformance limits are now due to:
#   - Mask image generation (not mask processing)
#   - Surface preparation
# TODO: Investigate Numpy array use directly within Pygame
# TODO: Investigate alpha.composite in PIL 2

import io, time, sys
import pygame
import picamera
import picamera.array
from PIL import Image, ImageStat, ImageOps, ImageDraw
import numpy as np
import os.path
from sys import argv

script, file_prefix = argv

# Set working frame size (multiples of 32h, 16v -- or padded to these)
# But we're not doing the post-crop, so... stick with %32 sizes
# Good sizes are 736, 800, 864, 896, 928, 960, 1024, 1056
# Best frame-rate compromise for a 1920x1080 display is probably 864 
size = width, height = 736, 736
# Should we display full screen, or windowed?
full_screen = 1

# Video settings
# Keep the video_framerate low to allow longer shutter speeds.
# Also, faster shutter speeds slow the whole system down. It's not clear why.
video_framerate = 4
# Juggle these a little - need buffer to be full before we start processing
# frames, so prerecord_seconds should not be shorter than buffer_length
buffer_length = 3
prerecord_seconds = 4

# Set output directory for manual and automatic framedumps
output_directory = "/home/pi/outputs"
# How often should we automatically output a frame to disk?
framedump_interval = 1000

# Default image processing settings
threshold_low = 120
threshold_high = 160

# ------------- END OF CONFIGURATION

# Runtime variables, leftover configuration, etc.
output_mode = 1
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
pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')

# Set up overlay mask image
# Oversize so it anti-aliases on scaledown
overmask_size = (width * 3, height *3)
overmask_centre = [ overmask_size[0] / 2 , overmask_size[1] / 2 ]
overmask_radius = overmask_size[0] /2 

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
    global output_mode
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

with picamera.PiCamera() as camera:
    camera.resolution = (width, height)
    camera.framerate = video_framerate
    # camera.rotation = video_rotation
    camera.video_stabilization = video_stabilization
    # camera.annotate_background = video_annotate_background
    # camera.annotate_frame_num = video_annotate_frame_num
    
    # Run the camera to capture initial exposure values
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
    
    # Now loop, within context of this camera object so we don't have to re-initialise
    
    # MAIN LOOP START
    with picamera.PiCameraCircularIO(camera, seconds=buffer_length) as stream:
        # Pre-populare the camera buffer. Need a short buffer so it's always overflowing
        # (with a deep buffer we'll see the same first frame each time)
        # (although we've a suspicion this isn't behaving as we think)
        camera.start_recording(stream, format='rgb')
        camera.wait_recording(prerecord_seconds)
        try:
            time_begin = time.time()
            while True:
                time_start = time.time()
                # Handle PyGame events (ie. keypress controls)
                handlePygameEvents()

                # ***** IMAGE CAPTURE *****
                # Lock the stream briefly
                with stream.lock:
                    for frame in stream.frames:
                        if (frame.complete): # ensure we get only a complete frame, just in case
                            stream.seek(frame.position)
                            # Read frame_size bytes from the circular buffer into a PIL Image object
                            frame_new = Image.frombytes('RGB', size, stream.read(frame.frame_size))
                        break # we only want the first frame from the buffer
                # stream.clear() # Reset the circular stream, so we never see this image again

                # We have our frame, so we've unlocked the circularIO stream,
                # which merrily continues recording in the background.
                # (via unicorns or threads or similar magic)

                # ***** YUV CONVERSION & EXTRACTION *****
                # Convert captured RGB image to YUV, and extract Y (brightness) component
                frame_yuv = frame_new.convert("YCbCr")
                frame_yuv_array = np.array(frame_yuv)
                frame_y = frame_yuv_array[0:width, 0:height, 0]

                # Output overall brightness calculation. Later, we'll use this to 
                # Handle flash frame discrimination
                frame_brightness = get_brightness(frame_new)

    			#~ mask = Image.fromarray(frame_y, "L")
    			#~ mask.save("mask-before.jpeg")

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
                
                # ***** OUTPUT FRAME STATS AND INFO *****
                time_taken = time.time() - time_start
                time_since_begin = time.time() - time_begin
                print "Frame %d in %.3f secs, at %.2f fps: shutter: %d, low: %d high: %d" % (frame_count, time_taken, (frame_count/time_since_begin), camera.shutter_speed, threshold_low, threshold_high)
                
                frame_count += 1
                
                if (frame_count % framedump_interval == 0):
                    framedump()
                
                # ***** /LOOP *****

        finally:
            camera.stop_recording()
