from io import BytesIO
from time import sleep, time
from picamera import PiCamera

my_stream = BytesIO()
camera = PiCamera()
camera.resolution = (768, 768)
camera.start_preview()
sleep(2)
start = time()
camera.capture(my_stream, 'jpeg')
elapsed = time() - start
print(elapsed)


