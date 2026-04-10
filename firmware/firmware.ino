#include <FastLED.h>

#define LED_PIN 15
#define LED_COUNT 3

#define SW1_PIN 14
#define SW2_PIN 12
#define SW3_PIN 13

CRGB leds[LED_COUNT];
bool isSWPressed[3] = {false,false,false};
int state[3] =  {0,0,0};

IRAM_ATTR void interruptSW1() {
  detachInterrupt(digitalPinToInterrupt(SW1_PIN));
  isSWPressed[0] = true;
}

IRAM_ATTR void interruptSW2() {
  detachInterrupt(digitalPinToInterrupt(SW2_PIN));
  isSWPressed[1] = true;
}
IRAM_ATTR void interruptSW3() {
  detachInterrupt(digitalPinToInterrupt(SW3_PIN));
  isSWPressed[2] = true;
}

void setup() {
  Serial.begin(115200);

  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  pinMode(SW3_PIN, INPUT_PULLUP);

  pinMode(LED_PIN, OUTPUT);
  FastLED.addLeds<NEOPIXEL, LED_PIN>(leds, LED_COUNT);

  attachInterrupt(digitalPinToInterrupt(SW1_PIN), interruptSW1, RISING);
  attachInterrupt(digitalPinToInterrupt(SW2_PIN), interruptSW2, RISING);
  attachInterrupt(digitalPinToInterrupt(SW3_PIN), interruptSW3, RISING);
  
  leds[0] = CRGB(0,200,0);
  leds[1] = CRGB(0,200,0);
  leds[2] = CRGB(0,200,0);
}

void loop() {
  int i=0;
  while(Serial.available()){
    char pcStatus = Serial.read();
    if(pcStatus >= 48){
      state[i] = int(pcStatus-48);
      if(state[i] == 0){
        leds[i] = CRGB(200,0,0);
      }else{
        leds[i] = CRGB(0,200,0);
      }
    }
    i++;
  }

  FastLED.show();
  if(isSWPressed[0]){
    Serial.println("0");
    isSWPressed[0] = false;
    if(state[0] == 0){
      state[0] = 1;
      leds[0] = CRGB(200,0,0);
    }else{
      state[0] = 0;
      leds[0] = CRGB(0,200,0);
    }
    FastLED.show();
    delay(250);
    attachInterrupt(digitalPinToInterrupt(SW1_PIN), interruptSW1, RISING);
  }
  if(isSWPressed[1]){
    Serial.println("1");
    isSWPressed[1] = false;
    if(state[1] == 0){
      state[1] = 1;
      leds[1] = CRGB(200,0,0);
    }else{
      state[1] = 0;
      leds[1] = CRGB(0,200,0);
    }
    FastLED.show();
    delay(250);
    attachInterrupt(digitalPinToInterrupt(SW2_PIN), interruptSW2, RISING);
  }
  if(isSWPressed[2]){
    Serial.println("2");
    isSWPressed[2] = false;
    if(state[2] == 0){
      state[2] = 1;
      leds[2] = CRGB(200,0,0);
    }else{
      state[2] = 0;
      leds[2] = CRGB(0,200,0);
    }
    FastLED.show();
    delay(250);
    attachInterrupt(digitalPinToInterrupt(SW3_PIN), interruptSW3, RISING);
  }
}
