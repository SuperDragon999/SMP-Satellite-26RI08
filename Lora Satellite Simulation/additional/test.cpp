//Code to test out the Serial Monitor
#include <Arduino.h>

void setup(){
    Serial.begin(921600);
}

void loop(){
    Serial.println("Hello World!");
    delay(100);
}