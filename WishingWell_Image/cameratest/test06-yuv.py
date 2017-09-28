from time import sleep, time
from picamera import PiCamera
from PIL import Image

camera = PiCamera()
camera.resolution = (768, 768)
camera.start_preview()
sleep(2)
start = time()
camera.capture('image.data', 'yuv')
elapsed = time() - start
print(elapsed)

