// Setup WiFi network, reporting local IP address to serial
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
}

// Maintain MQTT broker connection, subscribe to topics on (re)connect
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(scutterNameArray)) {
      Serial.println("connected");
      // Once connected, publish an announcement...
//      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("wishing/colour");
      client.subscribe("wishing/direction");
      client.subscribe("wishing/speed");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
