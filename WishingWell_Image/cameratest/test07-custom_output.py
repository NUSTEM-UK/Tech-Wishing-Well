import picamera

class MyOutput(object):
	def __init__(self):
		self.size = 0
	
	def write(self, s):
		self.size += len(s)
	
	def flush(self):
		print('%d bytes would have been written' % self.size)

with picamera.PiCamera() as camera:
	camera.resolution = (768, 768)
	camera.framerate = 60
	camera.start_recording(MyOutput(), format='yuv')
	camera.wait_recording(10)
	camera.stop_recording()

