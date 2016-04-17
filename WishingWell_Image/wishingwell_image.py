import io, time, sys
import pygame
import picamera
import picamera.array
from PIL import Image, ImageStat
from timer import Timer
import numpy as np

pygame.init()

# Set working frame size
size = width, height = 720, 720

# Initialise PyGame surface
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
pygame.display.flip()

# Initialise PIL image to black background
composite = Image.frombytes('RGB', size, "\x00" * width * height * 3)
composite = composite.convert('RGBA')

# Video settings, culled from example code (mostly not used - TODO cleanup)
video_framerate = 5
shutter_max = (1.0/video_framerate) * 1000000  # microsec exposure for shutter setting
shutter_min = 1000              			   # microsec exposure for shutter setting
print shutter_min, shutter_max
video_rotation = 180
video_port = False
video_stabilization = False
video_annotate_background = False
video_annotate_frame_num = False
perform_snapshot_capture = False
snapshot_capture_filename = "snapshot"

# Runtime variables
threshold_low = 60
threshold_high = 250
frame_count = 1
output_mode = 1

# Original transparency mask code: very slow, nasty edges but works well enough.
# No longer called in current version
def transparentify(image, threshold):
    """docstring for transparentify"""
    # With thanks to:
    # http://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent
	# This is the original algorithm, which is rather slow; steps through all of R,G,B values
	# to compute mask, all done in PIL. Numpy version is ~60x faster.
    data = image.getdata()
    newData = list()
    for item in data:
        if item[0] < threshold and item[1] < threshold and item[2] < threshold:
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)
    image.putdata(newData)
    return image

def handlePygameEvents():
    for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type is pygame.KEYDOWN:
                key_press = pygame.key.name(event.key)
                print key_press
                if key_press is "s":
                    camera.shutter_speed -= 1000
                    if camera.shutter_speed < shutter_min:
                        camera.shutter_speed = shutter_min
                    print "Shutter speed set to: %s" % camera.shutter_speed
                elif key_press is "w":
                    camera.shutter_speed += 1000
                    if camera.shutter_speed > shutter_max:
                        camera.shutter_speed = shutter_max
                    print "Shutter speed set to: %s" % camera.shutter_speed
                elif key_press is "e":
                    threshold_low += 1
                    if threshold_low > 255:
                        threshold_low = 255
                    print "threshold_low set to %i" % threshold_low
                elif key_press is "d":
                    threshold_low -= 1
                    if threshold_low < 0:
                        threshold_low = 0
                    print "threshold_low set to %i" % threshold_low
                elif key_press is "r":
                    threshold_high += 1
                    if threshold_high > 255:
                        threshold_high = 255
                    print "threshold_high set to %i" % threshold_high
                elif key_press is "f":
                    threshold_high -= 1
                    if threshold_high < 0:
                        threshold_high = 0
                    print "threshold_high set to %i" % threshold_high
                elif key_press is "m":
                    # Toggle output mode
                    output_mode += 1
                    if output_mode > 3:
                        output_mode = 1
                    
                # Check for left shift and allow rapid threshold changes
                if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    if key_press is "q":
                            sys.exit()
                    if key_press is "e":
                        threshold_low += 10
                        if threshold_low > 255:
                            threshold_low = 255
                        print "threshold_low set to %i" % threshold_low
                    elif key_press is "d":
                        threshold_low -= 10
                        if threshold_low < 0:
                            threshold_low = 0
                        print "threshold_low set to %i" % threshold_low
                    elif key_press is "r":
                        threshold_high += 10
                        if threshold_high > 255:
                            threshold_high = 255
                        print "threshold_high set to %i" % threshold_high
                    elif key_press is "f":
                        threshold_high -= 10
                        if threshold_high < 0:
                            threshold_high = 0
                        print "threshold_high set to %i" % threshold_high
                    # Check for SHIFT+P and if found, set working image to pure black again
                    elif key_press is "p":
                        print "*** STARTING OVER ***"
                        composite = Image.frombytes('RGB', size, "\x00" * width * height * 3)
                        composite = composite.convert('RGBA')

def get_brightness(image):
    """Return overall brightness value for image"""
    stat = ImageStat.Stat(image)
    return stat.rms[0]

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
    time.sleep(3)
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

    # Now loop, within context of this camera object. Ooh.
    
    while 1:
        # Handle PyGame events (ie. keypress controls)
        handlePygameEvents()
    
        with Timer() as t1:
            with picamera.array.PiRGBArray(camera, size=(width, height)) as stream:
                stream.truncate(0) # Nuke the existing stream and repopulate for new frame
                with Timer() as t_capture:
                    camera.capture(stream, 'rgb', use_video_port=video_port) # Capture YUV data to stream object
                    print "Frame %s captured" % frame_count
                print "==> Frame capture in %s s" % t_capture.secs
                with Timer() as t_rgb:
                    frame = Image.fromarray(stream.array, "RGB") # Grab the YUV data into a Pillow YCbCr image
                print "==> Frame from array to RGB in %s s" % t_rgb.secs
                with Timer() as t_convertYUV:
                    frameyuv = frame.convert("YCbCr")
                    frameyuv_array = np.array(frameyuv)
                    y = frameyuv_array[0:width,0:height,0] # Get just the y component as a numpy array
                print "==> YUV conversion & Y extraction in %s s" % t_convertYUV.secs
        print "=> Frame capture complete in %s s" % t1.secs
    
        # Output overall brightness calculation. Later, we'll use this to 
        # Handle flash frame discrimination
        print "frame brightness: %d" % (get_brightness(frame))
    
        # with Timer() as t2:
    	    # frame = transparentify(frame, threshold)
        # print "=> Frame transparentified in %s s" % t2.secs
    
        with Timer() as t2a:
			#~ mask = Image.fromarray(y, "L")
			#~ mask.save("mask-before.jpeg")
			#~ print "MAX MASK VALUE: %s" % np.amax(y)
			#~ print "MIN MASK VALUE: %s" % np.amin(y)

			# Index Y array for values below threshold_low
            low_clip_indices = y < threshold_low
            # Set values at those indices to zero (ie. transparent)
            y[low_clip_indices] = 0
            # Index y array for values above threshold_high
            high_clip_indices = y > threshold_high
            # Set values at those indices to 255 (ie. solid)
            y[high_clip_indices] = 255
            #~ y_clip = np.clip(y, 0, threshold)
            #~ print "POST-CLIP MAX MASK VALUE: %s" % np.amax(y)
            #~ print "POST-CLIP MIN MASK VALUE: %s" % np.amin(y)
            # Make mask image from Numpy array y
            mask = Image.fromarray(y, "L")
            #~ mask.save("mask-after.jpeg")
        #~ print "=> Clip processing %s s" %t2a.secs
    
        with Timer() as t3:
            # Convert captured frame to RGBA
            frame = frame.convert("RGBA")
            #~ print frame.format, frame.size
            #~ print mask.format, mask.size
            # Combine captured frame with rolling composite, via computed mask
    	    composite.paste(frame, (0,0), mask)
        #~ print "=> Frame composited in %s s" % t3.secs
    
        # Prepare the PyGame surface
        # Need to convert PIL image to string representation, then string to PyGame image. Ugh.
        # Mode switching doesn't work for now, but the stub is here.
        if output_mode is 1:
            # Default mode: display composite
            raw_str = composite.tostring("raw", 'RGBA')
            pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')
        elif output_mode is 2:
            # Display mask only. Doesn't work.
            raw_str = mask.tostring("raw", 'L')
            pygame.surface = pygame.image.fromstring(raw_str, size, 'P')
        elif output_mode is 3:
            # Display raw image (no composite). Doesn't work.
            raw_str = frame.tostring("raw", 'RGBA')
            pygame.surface = pygame.image.fromstring(raw_str, size, 'RGBA')
        
        # Finally, update the window
        screen.blit(pygame_surface, (0,0))
        pygame.display.flip()
        
        frame.close() # release the file handle. Should avoid the memory leak?
        # (I don't think there is a memory leak any more, but I daren't remove this without testing)
        frame_count += 1
        # and around we go again.
    
