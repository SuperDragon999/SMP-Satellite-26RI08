//edit!
#include <SPI.h>
#include <RadioLib.h>

#define LORA_CLK     12
#define LORA_MISO    13
#define LORA_MOSI    11
#define LORA_CS      10
#define LORA_RST     14
#define LORA_BUSY    9
#define LORA_DIO9    16

#define RGB_DATA_PIN 38
#define RGB_PWR_PIN  39

#define ID 0

LR1121 radio = new Module(LORA_CS, LORA_DIO9, LORA_RST, LORA_BUSY);

volatile bool packetReceived = false;

void setFlag() {
    packetReceived = true;
}

uint8_t currentSF = 7;
float currentBW = 125.0;

struct SatellitePayload {
    uint8_t identifier;
    uint32_t messageId;
    uint32_t telemetry;
    uint32_t telemetry2;
};

SatellitePayload rxData;

void setup() {
    Serial.begin(921600);
    pinMode(RGB_DATA_PIN, OUTPUT);
    digitalWrite(RGB_PWR_PIN, HIGH);

    SPI.begin(LORA_CLK, LORA_MISO, LORA_MOSI, LORA_CS);
    
    int state = radio.begin(
        915.0,       // Carrier Frequency (MHz)
        currentBW,   // Bandwidth (kHz)
        currentSF,   // Spreading Factor
        5,           // Coding Rate (4/5)
        0x12,        // Sync Word
        17           // TX Power (dBm)
    );

    if (state != RADIOLIB_ERR_NONE) {
        while (true) {
            neopixelWrite(RGB_DATA_PIN, 50, 0, 0); // Solid Red indicates initialization failure
            delay(200);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            delay(200);
        }
    }

    // Set the TCXO voltage configuration required by Core1121's internal reference crystal
    // The LR1121 uses DIO3 to supply the TCXO regulator. 1.6V is typical.
    state = radio.setTCXO(1.6);
    if (state != RADIOLIB_ERR_NONE) {
        while (true) {
            Serial.println("Configuration Failed!");
            neopixelWrite(RGB_DATA_PIN, 100, 0, 0); // Solid red blocks execution on setup error
            Serial.println(state);
            delay(200);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            delay(200);
        }
    }

    radio.setPacketReceivedAction(setFlag);
    radio.startReceive();
}

void loop() {
    if (packetReceived) {
        packetReceived = false;

        int state = radio.readData((uint8_t*)&rxData, sizeof(rxData));
        if (state == RADIOLIB_ERR_NONE) {
            //REDESIGN
            char json[128];
            snprintf(json, sizeof(json),
            "{\"type\":\"telemetry\",\"id\":%d,\"msg\":%lu,\"sf\":%d,\"bw\":%.1f,\"pdr_hint\":%d}",
            ID,
            rxData.telemetry,
            currentSF,
            currentBW,
            state == RADIOLIB_ERR_NONE ? 1 : 0);

            Serial.println(json);
            neopixelWrite(RGB_DATA_PIN, 0, 50, 0); // Green flashes indicate a complete successful tracking swap
        } else {
            neopixelWrite(RGB_DATA_PIN, 50, 0, 0); // Red flash for frame checksum or CRC failure
        }
        
        radio.startReceive();
    }
}