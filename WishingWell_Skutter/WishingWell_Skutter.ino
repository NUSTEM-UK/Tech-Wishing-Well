#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Servo.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = "wishingwell";
const char* password = "thinkphysics1";
// const char* mqtt_server = "gooeypi.local"; // Test this, see if it works.
const char* mqtt_server = "10.0.1.3";

String huzzahMACAddress;
String skutterNameString;
char skutterNameArray[25];

String subsTargetString;
char subsTargetArray[34];

bool active = false;

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

uint8_t target_r = 255;
uint8_t target_g = 255;
uint8_t target_b = 255;

bool in_transition = false;
uint32_t transition_timeRemaining = 0;
String transitionType = "";


void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(115200);
  setup_wifi();

  huzzahMACAddress = WiFi.macAddress();
  skutterNameString = "skutter_" + huzzahMACAddress;
  Serial.println(skutterNameString);
  skutterNameString.toCharArray(skutterNameArray, 25);
  subsTargetString = "wishing/" + skutterNameString;
  subsTargetString.toCharArray(subsTargetArray, 34);
  for (int i = 0 ; i < 34 ; i++) {
    Serial.print(subsTargetArray[i]);
  }
  Serial.println();
  
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
    
    /* TARGET CHANGED ********************************************/
    if (topicString == subsTargetString) {
      Serial.println(F("Skutter target signal"));
      // Check to see if this Skutter is disabled, else enable
      if (payloadString == "False") {
        active = false;
        Serial.println(F("This Skutter is now inactive"));
      } else {
        active = true;
        Serial.println(F("This Skutter is now ACTIVE!"));
      }
    }

    /* REVERSE CHANGED *******************************************/
    if ( (topicString == "wishing/direction") && active ) {
      if ( payloadString == "1" ) {
        servoReverse = false;
      } else if ( payloadString == "0" ) {
        servoReverse = true;
      }
      in_transition = true;
    }

    /* SERVO SPEED CHANGED ***************************************/
    if ( (topicString == "wishing/speed") && active ) {
      int speedPercent = payloadString.toInt();
      // GUI client gives percent speed, so need to map:
      selectedSpeed = map(speedPercent, 0, 100, 0, 90);
      in_transition = true;
    }

    if ( (topicString == "wishing/colour") && active ) {
      // Strip the leading #
      number = strtol(&payloadString[1], NULL, 16);
      // Bitshift to extract red / green / blue values, taken mostly from:
      // http://stackoverflow.com/questions/23576827/arduino-convert-a-sting-hex-ffffff-into-3-int
      r = number >> 16;
      g = number >> 8 & 0xFF;
      b = number & 0xFF;
      in_transition = true;
    }

    if ( (topicString == "wishing/time") && active ) {
      int transition_timeRemaining = payloadString.toInt();
    }

    if ( (topicString == "wishing/transition") && active ) {
      // Check for "wheel", else assume "fade" - basic error checking.
      if (payloadString == "wheel") {
        transitionType = "wheel";
      } else {
        transitionType = "fade";
      }
    }
    
    /* ACT ON SETTINGS *******************************************/
    // Likely need to move this to loop(), with a check for in_transition.
    // Otherwise, we're going to block the callback during transition execution,
    // and not respond to additional incoming messages.
    if (active) {
      Serial.println(F("----------------------------------------")); 
      Serial.println(F("Executing commanded changes:"));   
      setServoSpeed(servoReverse, selectedSpeed);
      setNeoPixelColour(r, g, b);
      Serial.println(F("========================================"));
    }

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

void setNeoPixelColour(uint8_t r, uint8_t g, uint8_t b) {
  // Assume a strip of NeoPixels, even though we're likely working with just one
  for (int i = 0; i < PIXEL_COUNT; ++i) {
    strip.setPixelColor(i, r, g, b);
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
}

