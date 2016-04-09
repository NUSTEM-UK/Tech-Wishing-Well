# the scutter dictionary
def scutter_update(self):
    print "Connecting to the MQTT"
    mqttc = mqtt.Client("python_pub")
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_18:FE:34:F4:D6:F4", self.scut1.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_18:FE:34:F4:D4:79", self.scut2.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_5C:CF:7F:0E:2C:EA", self.scut3.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_5C:CF:7F:01:59:76", self.scut4.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_18:FE:34:F4:D3:BD", self.scut5.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_5C:CF:7F:01:59:5B", self.scut6.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_5C:CF:7F:0E:35:2D", self.scut7.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_18:FE:34:FD:92:D1", self.scut8.checkState())
    mqttc.connect('localhost', 1883)
    mqttc.publish("wishing/Scutter_5C:CF:7F:0E:31:16", self.scut9.checkState())
    print "Update complete."