#!/usr/bin/env python
import io
import socket
import struct
import io, time, sys
import pygame
from PIL import Image, ImageStat, ImageOps, ImageDraw
import numpy as np
import os.path
from sys import argv

script, file_prefix = argv

# Set working frame size (multiples of 32h, 16v -- or padded to these)
# But we're not doing the post-crop, so... stick with %32 sizes
# Good sizes are 736, 800, 864, 896, 928, 960, 1024, 1056
# Best frame-rate compromise for a 1920x1080 display is probably 864 
size = width, height = 864, 864
# Should we display full screen, or windowed?
full_screen = 0

# Set output directory for manual and automatic framedumps
output_directory = "/Users/jonathan/Desktop/outputs"
# How often should we automatically output a frame to disk?
framedump_interval = 1000

# Default image processing settings
threshold_low = 120
threshold_high = 160

# ------------- END OF CONFIGURATION

# Runtime variables, leftover configuration, etc.
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
pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')

# Set up overlay mask image
# Oversize so it anti-aliases on scaledown
overmask_size = (width * 3, height *3)
overmask_centre = [ overmask_size[0] / 2 , overmask_size[1] / 2 ]
overmask_radius = overmask_size[0] /2 

# Start a socket listening for connections on 0.0.0.0:8000 
# (0.0.0.0 means all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

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
            if key_press == pygame.K_e:
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
                # Check for SHIFT+P and if found, set working image to pure black again
                elif key_press == pygame.K_p:
                    print "*** STARTING OVER ***"
                    composite = Image.frombytes('RGB', size, "\x00" * width * height * 3)
                    composite = composite.convert('RGBA')


# Set up mask image
drawOvermask()

# ***** START NETWORK CONNECTION
connection = server_socket.accept()[0].makefile('rb')
try:
    time_begin = time.time()
    while True:
        # ***** MAIN LOOP START *****
        time_start = time.time()
        
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, grab it as next_frame
        image_stream.seek(0)
        frame_new = Image.frombytes('RGB', size, image_stream.read(image_len))
        # frame_grab = Image.open(image_stream)
        # frame_new = frame_grab.convert('RGB')

        # ***** YUV CONVERSION & EXTRACTION *****
        # Convert captured RGB image to YUV, and extract Y (brightness) component
        frame_yuv = frame_new.convert("YCbCr")
        frame_yuv_array = np.array(frame_yuv)
        frame_y = frame_yuv_array[0:width, 0:height, 0]

        # Overall brightness calculation. 
        # Later, we'll use this to handle flash frame discrimination
        frame_brightness = get_brightness(frame_new)
        
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
        raw_str = composite.tobytes("raw", 'RGBA')
        pygame_surface = pygame.image.fromstring(raw_str, size, 'RGBA')
        
        # Finally, update the window
        screen.blit(pygame_surface, (0,0))
        pygame.display.flip()
        
        # Handle PyGame events (ie. keypress controls)
        handlePygameEvents()
        
        # ***** OUTPUT FRAME STATS AND INFO *****
        time_taken = time.time() - time_start
        time_since_begin = time.time() - time_begin
        print "Frame %d in %.3f secs, at %.2f fps, low: %d high: %d" % (frame_count, time_taken, (frame_count/time_since_begin), threshold_low, threshold_high)
        
        frame_count += 1
        
        if (frame_count % framedump_interval == 0):
            framedump()
            
        # ***** /LOOP *****

finally:
    connection.close()
    server_socket.close()