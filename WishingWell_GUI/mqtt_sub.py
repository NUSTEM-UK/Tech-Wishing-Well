import paho.mqtt.client as mqtt

def on_connect(client, userdata, rc):
	print "Connected with result code: " + str(rc)
	client.subscribe("wishing/colour")
	client.subscribe("wishing/direction")
	client.subscribe("wishing/speed")

def on_message(client, userdata, msg):
	print "Topic: ", msg.topic + '\nMessage: ' + str(msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('localhost', 1883)

client.loop_forever()
