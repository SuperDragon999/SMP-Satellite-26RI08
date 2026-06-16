#include <SPI.h>
#include <RadioLib.h>

#define LORA_CLK     12
#define LORA_MISO    13
#define LORA_MOSI    11
#define LORA_CS      10
#define LORA_RST     15
#define LORA_BUSY    9
#define LORA_DIO9    16

#define RGB_DATA_PIN 38
#define RGB_PWR_PIN  39

#define ID 1

struct SatellitePayload {
    uint8_t identifier;
    uint32_t messageId;
    uint32_t telemetry;
    uint32_t telemetry2;
};

struct AckPayload {
    uint8_t packetType;
    uint8_t identifier;
    uint32_t messageId;
    uint8_t targetSF;
    uint8_t targetBWCode;
};

SatellitePayload txData;
AckPayload ackData;
LR1121 radio = new Module(LORA_CS, LORA_DIO9, LORA_RST, LORA_BUSY);

uint8_t satSF = 7; // CHANGE BEFORE EACH TEST
float satBW = 125; // CHANGE BEFORE EACH TEST

void setup() {
    Serial.begin(921600);
    pinMode(RGB_DATA_PIN, OUTPUT);
    pinMode(RGB_PWR_PIN, OUTPUT);
    digitalWrite(RGB_PWR_PIN, HIGH);
    
    delay(100);    
    SPI.begin(LORA_CLK, LORA_MISO, LORA_MOSI);

    radio.tcxoVoltage = 1.6;
    // Initialization signature for RadioLib LR1121 standard syntax
    int state = radio.begin(
        915.0,       // Center Frequency (MHz)
        satBW,       // Bandwidth (kHz)
        satSF,       // Spreading Factor
        5,           // Coding Rate (4/5)
        0x12,        // Sync Word
        17,          // Output Power (dBm)
        8            // Preamble length
    );

    radio.setFrequency((double)(915 + 0.0220121799763));
    
    if (state != RADIOLIB_ERR_NONE) {
        while (true) {
            Serial.println("Configuration Failed!");
            neopixelWrite(RGB_DATA_PIN, 100, 0, 0); // Red-blue flashes on setup error, blocks initialization
            Serial.print("Error: ");
            Serial.println(state);
            delay(200);
            neopixelWrite(RGB_DATA_PIN, 0, 100, 0);
            delay(200);
        }
    }
}

uint32_t count = 0;
volatile long long loopStart;
void loop() {
    loopStart = millis();

    radio.standby();

    // 1. Compile system frame payload structures
    txData.identifier = ID;
    txData.messageId = count++;
    txData.telemetry = 123;
    txData.telemetry2 = 472;
    
    // 2. Dispatch telemetry
    int txState = radio.transmit((uint8_t*)&txData, sizeof(txData));
    yield();
    
    if (txState == RADIOLIB_ERR_NONE) {
        neopixelWrite(RGB_DATA_PIN, 0, 0, 20); // Blue indicates down-link transmission confirmed
        delay(20);
        neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
    } else {
        neopixelWrite(RGB_DATA_PIN, 50, 0, 0);
    }
    
    long long end = millis();
    if (end - loopStart <= 2500){
        delay(2500 - (end - loopStart)); //2.5 second gap
    }
}