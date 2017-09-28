# Python camera notes

## test01 -- Capture to file
For 768 x 768 resoution, takes about 0.58 sec to process and output.

## test02 -- Stream capture
Same resoution: about 0.55 sec to capture to in-memory stream. Ouch.

## test03 -- stream to PIL
Adds very little overhead - 0.56 sec to capture to PIL object.

## test04 -- capture_continuous
Appears to be terrible (~1fps?), but thats mostly the processing to JPEG?

## test05 -- capture to numpy array
Still about 0.54 secs

## test06 -- capture to YUV
Still 0.54 sec

## test10 -- capture_continuous
Well, this is simpler. Based on capturing to an in-memory stream on a continuous basis, then just truncating the buffer after every frame is processed.
With BGR format and 768x768 resolution, runs around 9.2fps.
With RGB format, near 12fps.
YUV arrays are a different shape, so not yet tested

This is a useful list of common errors: https://www.pyimagesearch.com/2016/08/29/common-errors-using-the-raspberry-pi-camera-module/
Capturing to a YUV array: http://picamera.readthedocs.io/en/latest/recipes2.html
(note that conversion to RGB using this recipe two years ago failed with colour shifts.
    May now be more effective or efficient. We ultimately want YUV data for mask generation,
    so it likely makes sense to run the capture in that space and convert to RGB than go
    the other way only to throw most of the data away.)

Oh, blimey -- that's with the default camera framerate, which turns out to be 12.
Set camera.framerate(15), and... we hit 14.8fps at 768px square.
framerate(20), however, yields 11 fps and an odd cadence. So there are bandwidth limits coming in here.

RGB, 15fps camera, 864px square: yields about 13fps, with spikes.
