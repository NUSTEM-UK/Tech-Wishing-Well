# Tech-Wishing-Well
The [Think Physics](http://thinkphysics.org) [Technology Wishing Well](http://thinkphysics.org/activity/technology-wishing-well/) being showcased at [Maker Faire UK 2016](http://www.makerfaireuk.com), April 23rd & 24th, Centre for Life, Newcastle.

See the links above for background information.

As of March 2017 we *still* haven't found the time to write all this up properly. That will come (promise!), but for now here's the skinny:

## Building your own Wishing Well

There are many moving parts to the Well, but to make your own you really only need:

* A Raspberry Pi 2 or 3.
* A Pi camera

...actually, that's it. It's also helpful - though not strictly essential - to have:

* Some way of supporting the Pi/Camera. 1 metre-long camera ribbons cables help enormously!
* A turntable. Ikea sell good, cheap turntable for cake decoration.
* Some way of motorising the turntable. Try rigging up something using a [right-angle geared motor](https://www.kitronik.co.uk/2547-right-angle-geared-hobby-motor.html), perhaps like the [little turntables we made for our Light Wall](https://nustem.uk/activity/light-wall/) display.
* Some light sources - we like watch batteries and a range of coloured LEDs - or interesting coloured objects to scatter on the turntable.

Now download this source code archive:

    git clone https://github.com/ThinkPhysics/Tech-Wishing-Well

The main script assumes the existence of an output directory in your user home, so `mkdir ~/output` to create that. Now, the script you need is in `WishingWell_Image/`, so `cd` there and:

    python wishingwell_image.py *filename_prefix*

Use whatever filename prefix you wish - images created in the output directory will use that as a base.

You should see a preview of your camera output for a few second (to stablise and lock exposure settings), then you'll see a circular aperture with, most likely, a bunch of mess in it. The system responds to several keyboard commands:

    m : switch Mode between full-screen and windowed. It's easier to see what's going on with the image processing in windowed mode.
    P : (that's left-shift + p): reset display. Chosen to be hard to hit by accident.
    w/s : Increase/decrease exposure time. (hold left shift to move in larger steps). A longer exposure will give longer light trails, but more light overall.
    e/d : Increase/decrease lower cutoff. Changes the threshold brightness below which the image is turned transparent.
    r/f : Increase/decrease upper cutoff. Changes the threshold brightness above which the image is assumed to be opaque.
    o : output the current image to the outputs directory.

There's a lot of documentation in comments through the `wishingwell_image.py` code - so it's worth reading through there. In particular, you may need to experiment with capture resolution in order to fit the image within your screen display.

The rest of the files in this repository do things like:

* `WishingWell_Skutter/` : code to run the rotating-light robots we built, which are based on Adafruit Huzzah / ESP8266 boards and commanded over MQTT.
* `WishingWell_GUI/` : a front-end to control commands sent to the Skutter robots.
* `WishingWell_Twitter/` : code to run our camera booth.
* `docs/` : almost no documentation, because we haven't written it yet.

## What's next

Things to do:

* There are many better ways for us to access the camera. In particular, I want to play with the fast mode of `raspistill` and see if bouncing images off the SD card is actually quicker than the pure Python API of PiCamera.
* Document a tabletop build properly.
* Photograph the assembled Well properly. This is surprisingly hard to do, and the main reason we've only got this skeletal write-up so far!
* Experiment with very high-resolution / long exposure imagery.
* Make a wider range of LED robots, with different behaviours and lighting patterns.
