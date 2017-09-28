# Python3 only: python2 will only handle 1-d numpy arrays

from io import BytesIO
from time import sleep, time
import picamera
from PIL import Image
import numpy as np

with picamera.PiCamera() as camera:
	camera.resolution = (768, 768)
	camera.framerate = 24
	#camera.start_preview()
	sleep(2)
	start = time()
	output = np.empty((768, 768, 3), dtype=np.uint8)
	camera.capture(output, 'rgb')
	elapsed = time() - start
	print(elapsed)

