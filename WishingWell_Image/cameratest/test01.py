from time import sleep, time
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (768, 768)
camera.start_preview()
sleep(2)
start = time()
camera.capture('foo.jpg')
elapsed = time() - start
print(elapsed)

