#!/usr/bin/env python
import io
import time
import threading
import pygame
import picamera
import picamera.array
from PIL import Image, ImageStat, ImageOps, ImageDraw
import numpy as np

size = width, height = 736, 736
full_screen = 0
video_framerate = 8

threshold_low = 120
threshold_high = 160
shutter_max = (1.0/video_framerate) * 1000000
shutter_min = 1000
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

class ImageProcessor(threading.Thread):
    def __init__(self, owner):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.owner = owner
        self.start()

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    frame_new = Image.frombytes('RGB', size, stream.read(frame.frame_size))
                    print("GOT FRAME")
                    frame_yuv = frame_new.convert('YCbCr')
                    frame_yuv_array = np.array(frame_yuv)
                    frame_y = frame_yuv_array[0:width, 0:height, 0]
                    low_clip_indices = frame_y < threshold_low
                    frame_y[low_clip_indices] = 0
                    high_clip_indices = frame_y > threshold_high
                    frame_y[high_clip_indices] = 255
                    
                    mask = Image.fromarray(frame_y, "L")
                    frame_new = frame_new.convert("RGBA")
                    composite.paste(frame_new, (0,0), mask)
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #self.owner.done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the available pool
                    with self.owner.lock:
                        self.owner.pool.append(self)

class ProcessOutput(object):
    def __init__(self):
        self.done = False
        # Construct a pool of 4 image processors along with a lock
        # to control access between threads
        self.lock = threading.Lock()
        self.pool = [ImageProcessor(self) for i in range(4)]
        self.processor = None

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame; set the current processor going and grab
            # a spare one
            if self.processor:
                self.processor.event.set()
            with self.lock:
                if self.pool:
                    self.processor = self.pool.pop()
                else:
                    # No processors available, we'll have to skip
                    # this frame; you may want to print a warning
                    # here to see whether you hit this case 
                    self.processor = None
                    print(">>> NO PROCESSOR: Frame skip")
        if self.processor:
            self.processor.stream.write(buf)

    def flush(self):
        # When told to flush (this indicates end of recording), shut
        # down in an orderly fashion. First, add the current processor
        # back to the pool
        if self.processor:
            with self.lock:
                self.pool.append(self.processor)
                self.processor = None
        # Now, empty the pool, joining each thread as we go
        while True:
            with self.lock:
                try:
                    proc = self.pool.pop()
                except IndexError:
                    pass # pool is empty
            proc.terminated = True
            proc.join()

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
    camera.iso = 100
    camera.start_preview()
    time.sleep(int(20/video_framerate))
    # Fix values
    camera.shutter_speed = camera.exposure_speed
    brightness = camera.brightness
    camera.exposure_mode = 'off'
    white_balance = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = white_balance
    camera.stop_preview()
    
    drawOvermask()
    
    output = ProcessOutput()
    camera.start_recording(output, format='mjpeg')
    while not output.done:
        handlePygameEvents()
        composite.paste(overmask, (0,0), ImageOps.invert(overmask))
        raw_str = composite.tostring("raw", 'RGBA')
        pygame_surface = pygame.image.fromstring(raw_string, size, 'RGBA')
        screen.blit(pygame_surface, (0,0))
        pygame.display.flip()
        camera.wait_recording(1)
    camera.stop_recording()
