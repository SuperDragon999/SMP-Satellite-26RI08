#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>

#define CS 10
#define RESET 15
#define BUSY 21
#define DIO1 16

#define RGB_DATA_PIN 38
#define RGB_PWR_PIN  39

SX1262 radio = new Module(CS, DIO1, RESET, BUSY);

void setup() {
    Serial.begin(921600);
    pinMode(RGB_DATA_PIN, OUTPUT);
    pinMode(RGB_PWR_PIN, OUTPUT);
    digitalWrite(RGB_PWR_PIN, HIGH);

    SPI.begin(12, 13, 11, CS);

    pinMode(DIO1, INPUT_PULLUP);
    pinMode(BUSY, INPUT);

    delay(1000);

    Serial.println("Starting radio...");

    int state = radio.begin(923.0);

    Serial.print("State = ");
    Serial.println(state);
    if (state != RADIOLIB_ERR_NONE) {
        while (true) {
            neopixelWrite(RGB_DATA_PIN, 100, 0, 0); // Solid red blocks execution on setup error
            Serial.println(state);
            delay(200);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            delay(200);
        }
    }
}

void loop() {

}