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
from PIL import Image, ImageStat
from timer import Timer
import numpy as np

pygame.init()

# Set working frame size (multiples of 32h, 16v -- or padded to these)
# But we're not doing the post-crop, so... stick with %32 sizes
size = width, height = 736, 736
# frame size is queried directly from the CircularIO object
# frame_width = (width + 31) // 32 * 32
# frame_height = (height + 15) // 16 * 16
# framesize = frame_width * frame_height * 3 # for RGB (YUV is funky here, 4:2:0 sampled -- see docs)

# Initialise PyGame surface
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
pygame.display.flip()

# Initialise PIL image to black background
composite = Image.frombytes('RGB', size, "\x00" * width * height * 3)
composite = composite.convert('RGBA')
raw_str = composite.tostring("raw", 'RGBA')
pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')

# Video settings, culled from example code (mostly not used - TODO cleanup)
video_framerate = 4
shutter_max = (1.0/video_framerate) * 1000000  # microsec exposure for shutter setting
shutter_min = 1000              			   # microsec exposure for shutter setting
print shutter_min, shutter_max
video_rotation = 180
video_port = True
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

def get_brightness(image):
    """Return overall brightness value for image"""
    stat = ImageStat.Stat(image)
    return stat.rms[0]

def handlePygameEvents():
    global threshold_low
    global threshold_high
    global output_mode
    global composite
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

    # Now loop, within context of this camera object so we don't have to re-initialise
    
    # MAIN LOOP START
    with picamera.PiCameraCircularIO(camera, seconds=1) as stream:
        # Pre-populare the camera buffer. Need a short buffer so it's always overflowing
        # (with a deep buffer we'll see the same first frame each time)
        camera.start_recording(stream, format='rgb')
        print "CAMERA RECORDING"
        camera.wait_recording(1)
        print "1-SECOND BUFFER RECORDED"
        try:
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

                time_capture = time.time() - time_start
                print "Capture complete in %.3f secs" % time_capture
                # We have our frame, so we've unlocked the circularIO stream,
                # which merrily continues recording in the background.
                # (via unicorns or threads or similar magic)

                # ***** YUV CONVERSION & EXTRACTION *****
                # Convert captured RGB image to YUV, and extract Y (brightness) component
                frame_yuv = frame_new.convert("YCbCr")
                frame_yuv_array = np.array(frame_yuv)
                frame_y = frame_yuv_array[0:width, 0:height, 0]
            
                time_yuv = time.time() - time_capture
                print "YUV processing complete in %.3f secs" % time_yuv

                # Output overall brightness calculation. Later, we'll use this to 
                # Handle flash frame discrimination
                frame_brightness = get_brightness(frame_new)
                
                time_brightness = time.time() - time_yuv
                print "Brightness calculation complete in %.3f secs" % time_brightness

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
                
                time_mask = time.time() - time_brightness
                print "Mask processing complete in %.3f secs" % time_brightness

                # Make mask image from Numpy array frame_y
                mask = Image.fromarray(frame_y, "L")
                # mask.save("mask-after.jpeg")
    
                time_maskImage = time.time() - time_mask
                print "Mask image generation complete in %.3f secs" % time_maskImage

                # ***** COMPOSITE NEW FRAME *****

                # Convert captured frame to RGBA
                frame_new = frame_new.convert("RGBA")
                
                # Combine captured frame with rolling composite, via computed mask
                # TODO: Check this is really doing what we think it is
                composite.paste(frame_new, (0,0), mask)

                time_composite = time.time() - time_maskImage
                print "Compositing complete in %.3f secs" % time_composite

                # ***** DISPLAY NEW FRAME *****
    
                # Prepare the PyGame surface
                # Need to convert PIL image to string representation, then string to PyGame image. Ugh.
                # Mode switching doesn't work for now, but the stub is here.
                if output_mode is 1:
                    # Default mode: display composite
                    # pygame.surfarray.blit_array(pygame_surface, composite)
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
                
                time_surface = time.time() - time_composite
                print "Surface preparation complete in %.3f secs" % time_surface

                # Finally, update the window
                screen.blit(pygame_surface, (0,0))
                pygame.display.flip()
                
                time_blit = time.time() - time_surface
                print "Blit done in %.3f secs" % time_blit

                time_taken = time.time() - time_start
                print "Frame %d processed in %.3f secs, at %.2f fps" % (frame_count, time_taken, (1/time_taken))
                print "========================================="
                frame_count += 1
                # and around we go again.

        finally:
            camera.stop_recording()
