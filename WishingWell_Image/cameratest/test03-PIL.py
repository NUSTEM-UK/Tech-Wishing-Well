from io import BytesIO
from time import sleep, time
from picamera import PiCamera
from PIL import Image

my_stream = BytesIO()
camera = PiCamera()
camera.resolution = (768, 768)
camera.start_preview()
sleep(2)
start = time()
camera.capture(my_stream, format='jpeg')
my_stream.seek(0)
image = Image.open(my_stream)
elapsed = time() - start
print(elapsed)

