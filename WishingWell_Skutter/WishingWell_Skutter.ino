// Code for 'Skutters' - Adafruit Huzzahs which control the servo they're mounted on, and
// a NeoPixel RGB LED.
// Messages passed from a local network-hosted MQTT server, controlled via the WishingWell-GUI app.
// 
// This code needs substantial cleanup... but it does work.
// NB. Use v.2.2 of the Arduino ESP8266 library; v2.1 has a horrid bug which crashes with Servo.
//
// Jonathan Sanderson, Northumbria University, Newcastle UK.
// for Maker Faire UK, April 2016.
// Code for 'Skutters' - Adafruit Huzzahs which control the servo they're mounted on, and
// a NeoPixel RGB LED.
// Messages passed from a local network-hosted MQTT server, controlled via the WishingWell-GUI app.
// 
// This code needs substantial cleanup... but it does work.
// NB. Use v.2.2 of the Arduino ESP8266 library; v2.1 has a horrid bug which crashes with Servo.
//
// Jonathan Sanderson, Northumbria University, Newcastle UK.
// for Maker Faire UK, April 2016.

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

int servo_speed = 90;
bool servoReverse = false;
int selectedSpeed = 0;
int current_speed = 0;
String colourSelected = String("#FFFFFF");

uint32_t number = 16777215;
uint8_t r = 255;
uint8_t g = 255;
uint8_t b = 255;

uint8_t start_r = r;
uint8_t start_g = g;
uint8_t start_b = b;

uint8_t target_r = r;
uint8_t target_g = g;
uint8_t target_b = b;

int start_speed = selectedSpeed;
int target_speed = selectedSpeed;

bool in_transition = false;
uint32_t time_start = millis(); // Start time of commanded transition
uint32_t time_end = millis(); // End time of a commanded transition
uint32_t time_current = millis(); // Recalculated in transition loop
uint32_t transition_time = 5;
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
  myservo.write(servo_speed); // Set to zero speed so there's no servo kick on boot. Doesn't work
  pinMode(PIN_LED_BLUE, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  strip.begin();
  setNeoPixelColour(r, g, b);
  strip.show();
  
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  /* ACT ON SETTINGS *******************************************/
  
  if (active && in_transition) {
    time_current = millis();
    Serial.print(target_r);
    Serial.print(" ");
    Serial.println(start_r);
    if (time_current < time_end) {


      int interpolate(int start_value, int target_value, int start_time, int end_time, int current_time) {
      r = interpolate(start_r, target_r, start_time, time_end, time_current);
      g = interpolate(start_g, target_g, start_time, time_end, time_current);
      b = interpolate(start_b, target_b, start_time, time_end, time_current);
      
      Serial.print(F("TRANSITION "));
      Serial.print(time_current - time_start);
      Serial.print(F(" of "));
      Serial.print(time_end-time_start);
      Serial.print(F(" Colour setting: "));
      Serial.print(r);
      Serial.print(F(" "));
      Serial.print(g);
      Serial.print(F(" "));
      Serial.println(b);
      setNeoPixelColour(r, g, b);
    } else {
      // Ensure we actually reach targets
      setNeoPixelColour(target_r, target_g, target_b);

      // Reset colours for next target
      start_r = target_r;
      start_g = target_g;
      start_b = target_b;

      in_transition = false; // We're done; omit this path and wait for next command
      
    }
    delay(50);
  }

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

    /* COLOUR CHANGE *********************************************/
    if ( (topicString == "wishing/colour") && active ) {
      // Strip the leading #
      number = strtol(&payloadString[1], NULL, 16);
      // Bitshift to extract red / green / blue values, taken mostly from:
      // http://stackoverflow.com/questions/23576827/arduino-convert-a-sting-hex-ffffff-into-3-int
      target_r = number >> 16;
      target_g = number >> 8 & 0xFF;
      target_b = number & 0xFF;
      in_transition = true;
    }

    /* TRANSITION TIME CHANGE ************************************/
    if ( (topicString == "wishing/time") && active ) {
      transition_time = payloadString.toInt();
    }

    if ( (topicString == "wishing/transition") && active ) {
      // Check for "wheel", else assume "fade" - basic error checking.
      if (payloadString == "wheel") {
        transitionType = "wheel";
      } else {
        transitionType = "fade";
      }
    }

    // Calculate transition endpoints, so we're not doing that in the main loop
    time_start = millis();
    time_end = time_start + (transition_time * 1000);
    start_speed = servo_speed;
    target_speed = getServoSpeed(servoReverse, selectedSpeed);
    
    // Output diagnostics so we know the command was received
    Serial.println(F("----------------------------------------")); 
    Serial.println(F("Changes commanded:"));

    Serial.print(F("Transition "));
    Serial.print(transitionType);
    Serial.print(F(" in "));
    Serial.print(transition_time);
    Serial.print(F(" seconds. Starting at "));
    Serial.print(time_start);
    Serial.print(F(" ending at "));
    Serial.println(time_end);
  
    if (servoReverse) {
      Serial.print(F("Reverse "));
      Serial.println(servo_speed);
    } else {
      Serial.print(F("Forward "));
      Serial.println(servo_speed);
    }
  
    Serial.print(F("Colour target: "));
    Serial.print(target_r);
    Serial.print(F(" "));
    Serial.print(target_g);
    Serial.print(F(" "));
    Serial.println(target_b);
    
    Serial.println(F("========================================"));

 }


/* Handle servo speed and direction changes **********************/
void setServoSpeed(bool servoReverse, int selectedSpeed){
  if (servoReverse) {
    servo_speed = 90 - selectedSpeed;
  } else {
    servo_speed = 90 + selectedSpeed;
  }
  myservo.write(servo_speed);
}

int getServoSpeed(bool servoReverse, int selectedSpeed) {
  if (servoReverse) {
    servo_speed = 90 - selectedSpeed;
    Serial.print(F("Reverse "));
    Serial.println(servo_speed);
  } else {
    servo_speed = 90 + selectedSpeed;
    Serial.print(F("Forward "));
    Serial.println(servo_speed);
  }
  return servo_speed;
}

int interpolate(int start_value, int target_value, int start_time, int end_time, int current_time) {
  float start_value_float = (float) start_value;
  float target_value_float = (float) target_value;
  float calculated_value_float;
  int caluclated_value_int;

  if ( target_value_float < start_value_float ) {
    calculated_value_float = ( (start_value_float - target_value_float) / (float)(end_time - start_time) * (float)(current_time - start_time);
  } else {
    calculated_value_float = ( (target_value_start - start_value_float) / (float)(end_time - start_time) * (float)(current_time - start_time);
  }

  calucated_value_int = (int) calculated_value_float;
  return calculated_value_int;
  
}      

void setNeoPixelColour(uint8_t r, uint8_t g, uint8_t b) {
  int i;
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

