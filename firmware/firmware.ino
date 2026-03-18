//#include <FastLED.h>

#define LED_PIN 15
#define LED_COUNT 3

#define SW1_PIN 14
#define SW2_PIN 12
#define SW3_PIN 13

//CRGB leds[LED_COUNT];
bool isSWPressed[3] = {false,false,false};

ICACHE_RAM_ATTR void interruptSW1() {
  isSWPressed[0] = true;
}

ICACHE_RAM_ATTR void interruptSW2() {
  isSWPressed[1] = true;
}
ICACHE_RAM_ATTR void interruptSW3() {
  isSWPressed[2] = true;
}

void setup() {
  Serial.begin(115200);

  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  pinMode(SW3_PIN, INPUT_PULLUP);

  pinMode(LED_PIN, OUTPUT);
  //FastLED.addLeds<NEOPIXEL, LED_PIN>(leds, LED_COUNT);

  attachInterrupt(digitalPinToInterrupt(SW1_PIN), interruptSW1, RISING);
  attachInterrupt(digitalPinToInterrupt(SW2_PIN), interruptSW2, RISING);
  attachInterrupt(digitalPinToInterrupt(SW3_PIN), interruptSW3, RISING);
}

void loop() {
  delay(100);
  if(isSWPressed[0]){
    Serial.println("button 1 pressed");
    isSWPressed[0] = false;
  }
  if(isSWPressed[1]){
    Serial.println("button 2 pressed");
    isSWPressed[1] = false;
  }
  if(isSWPressed[2]){
    Serial.println("button 3 pressed");
    isSWPressed[2] = false;
  }

}
