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
threshold_low = 120
threshold_high = 160
frame_count = 1
output_mode = 1

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
            # print key_press # For diagnostic purposes, but messes up output
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
                elif key_press is "s":
                    if (camera.shutter_speed - 10000) > shutter_min:
                        camera.shutter_speed -= 10000
                    print "Shutter speed set to: %s" % camera.shutter_speed
                elif key_press is "w":
                    if (camera.shutter_speed + 10000) < shutter_max:
                        camera.shutter_speed += 10000
                    print "Shutter speed set to: %s" % camera.shutter_speed
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
                
                # Finally, update the window
                screen.blit(pygame_surface, (0,0))
                pygame.display.flip()
                
                frame_count += 1
                time_taken = time.time() - time_start
                time_since_begin = time.time() - time_begin
                print "Frame %d in %.3f secs, at %.2f fps: shutter: %d, low: %d high: %d" % (frame_count, time_taken, (frame_count/time_since_begin), camera.shutter_speed, threshold_low, threshold_high)
                # and around we go again.

        finally:
            camera.stop_recording()
