#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Servo.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = "WishingWell";
const char* password = "thinkphysics1";
const char* mqtt_server = "192.168.1.101";

String huzzahMACAddress;
String scutterNameString;
char scutterNameArray[25];

WiFiClient espClient;
PubSubClient client(espClient);

#define PIN_SERVO 12
#define PIN_PIXEL 5
#define PIN_LED_BLUE 2
#define PIN_LED_RED 0

#define PIXEL_COUNT 1

Servo myservo;
Adafruit_NeoPixel strip(PIXEL_COUNT, PIN_PIXEL, NEO_GRB + NEO_KHZ800);

long lastMsg = 0;
char msg[50];
int value = 0;

int servoPos = 90;
bool servoReverse = false;
int selectedSpeed = 0;
String colourSelected = String("#FFFFFF");

uint32_t number = 16777215;
uint8_t r = 255;
uint8_t g = 255;
uint8_t b = 255;


void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(115200);
  setup_wifi();

  huzzahMACAddress = WiFi.macAddress();
  scutterNameString = "Scutter_" + huzzahMACAddress;
  Serial.println(scutterNameString);
  scutterNameString.toCharArray(scutterNameArray, 25);
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  myservo.attach(PIN_SERVO);
  myservo.write(servoPos); // Set to zero speed so there's no servo kick on boot. Doesn't work
  pinMode(PIN_LED_BLUE, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  strip.begin();
  strip.show();
  
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

//  long now = millis();
//  if (now - lastMsg > 2000) {
//    lastMsg = now;
//    ++value;
//    snprintf (msg, 75, "hello world #%ld", value);
////    Serial.print("Publish message: ");
////    Serial.println(msg);
//    client.publish("outTopic", msg);
//  }
}

void callback(char* topic, byte* payload, unsigned int length) {

    // callback variable length gives us the length of the payload
    String payloadString;
    for (int i = 0; i < length; i++) {
      payloadString += String((char)payload[i]);
    }

    // for the topic, we need to call strlen to find the length
    String topicString;
    for (int i = 0; i < strlen(topic); i++) {
      topicString += String((char)topic[i]);
    }

    // Debug: print the (processed) received message to serial
    Serial.print(F("Message arrived ["));
    Serial.print(topicString);
    Serial.print(F("] "));
    Serial.println(payloadString);

    // Now handle the possible messages, matching on topic

    /* REVERSE CHANGED *******************************************/
    if (topicString == "wishing/direction") {
      if ( payloadString == "1" ) {
        servoReverse = false;
      } else if ( payloadString == "0" ) {
        servoReverse = true;
      }
    }

    /* SERVO SPEED CHANGED ***************************************/
    if (topicString == "wishing/speed") {
      int speedPercent = payloadString.toInt();
      // GUI client gives percent speed, so need to map:
      selectedSpeed = map(speedPercent, 0, 100, 0, 90);
    }

    if (topicString == "wishing/colour") {
      // Strip the leading #
      number = strtol(&payloadString[1], NULL, 16);
      // Bitshift to extract red / green / blue values, taken mostly from:
      // http://stackoverflow.com/questions/23576827/arduino-convert-a-sting-hex-ffffff-into-3-int
      r = number >> 16;
      g = number >> 8 & 0xFF;
      b = number & 0xFF;
    }
    
    /* ACT ON SETTINGS *******************************************/
    Serial.println(F("----------------------------------------")); 
    Serial.println(F("Executing commanded changes:"));   
    setServoSpeed(servoReverse, selectedSpeed);
    // Assume a strip of NeoPixels, even though we're likely working with just one
    for (int i = 0; i < PIXEL_COUNT ; i++) {
      strip.setPixelColor(i, r, g, b);
      Serial.print("Pixel ");
      Serial.print(i);
      Serial.print(" set to ");
      Serial.print(r);
      Serial.print(" ");
      Serial.print(g);
      Serial.print(" ");
      Serial.println(b);
    }
    strip.show();
    Serial.println(F("========================================"));
    

//   Switch on the LED if a 1 was received as first character
    if ((char)payload[0] == '1') {
      digitalWrite(BUILTIN_LED, LOW);   // Turn the LED on (Note that LOW is the voltage level
      // but actually the LED is on; this is because
      // it is acive low on the ESP-01)
    } else {
      digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED off by making the voltage HIGH
    }
 }


/* Handle servo speed and direction changes **********************/
void setServoSpeed(bool servoReverse, int selectedSpeed){
  if (servoReverse) {
    servoPos = 90 - selectedSpeed;
    Serial.print(F("Reverse "));
    Serial.println(servoPos);
  } else {
    servoPos = 90 + selectedSpeed;
    Serial.print(F("Forward "));
    Serial.println(servoPos);
  }
  myservo.write(servoPos);
}
