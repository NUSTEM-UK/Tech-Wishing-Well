import io
import socket
import struct
import time
import picamera

# Connect a client socket to quernvii:8000
client_socket = socket.socket()
client_socket.connect(('QuernVII.local', 8000))

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (864, 864)
        camera.framerate = 12
        camera.start_preview()
        time.sleep(3)
        camera.stop_preview()
                
        # Note the start time and construct a stream to hold image data temporarily
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'rgb', use_video_port=True):
            # Write length of capture to the stream & flush
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send the image data
            stream.seek(0)
            connection.write(stream.read())
            # Reset stream for next capture
            stream.seek(0)
            stream.truncate()
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
        
