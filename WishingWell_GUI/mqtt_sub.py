import paho.mqtt.client as mqtt

def on_connect(client, userdata, rc):
	print "Connected with result code: " + str(rc)

	#client.subscribe("wishing/Scutter_18:FE:34:F4:D6:F4")
	#client.subscribe("wishing/Scutter_18:FE:34:F4:D4:79")
	#client.subscribe("wishing/Scutter_5C:CF:7F:0E:2C:EA")
	#client.subscribe("wishing/Scutter_5C:CF:7F:01:59:76")
	#client.subscribe("wishing/Scutter_18:FE:34:F4:D3:BD")
	#client.subscribe("wishing/Scutter_5C:CF:7F:01:59:5B")
	#client.subscribe("wishing/Scutter_5C:CF:7F:0E:35:2D")
	#client.subscribe("wishing/Scutter_18:FE:34:FD:92:D1")
	client.subscribe("wishing/Scutter_5C:CF:7F:0E:31:16")
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
