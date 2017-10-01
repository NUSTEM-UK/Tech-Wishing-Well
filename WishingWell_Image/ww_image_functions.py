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