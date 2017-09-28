from time import sleep, time
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (768, 768)
camera.start_preview()
sleep(2)
start = time()
for filename in camera.capture_continuous('img{counter:03d}.jpg'):
	print('Captured %s' % filename)
	elapsed = time() - start
print(elapsed)

