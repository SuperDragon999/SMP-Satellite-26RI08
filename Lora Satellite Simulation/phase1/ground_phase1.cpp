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

uint8_t currentSF = 10; // CHANGE BEFORE EACH TEST
float currentBW = 500; // CHANGE BEFORE EACH TEST

struct SatellitePayload {
    uint8_t identifier;
    uint32_t messageID;
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
            Serial.println("Configuration failed!");
            neopixelWrite(RGB_DATA_PIN, 100, 0, 0); // Red-blue flashes indicates initialization failure
            delay(200);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            delay(10);
            neopixelWrite(RGB_DATA_PIN, 0, 100, 0);
            delay(200);
        }
    }

    // Set the TCXO voltage configuration required by Core1121's internal reference crystal
    // The LR1121 uses DIO3 to supply the TCXO regulator. 1.6V is typical.
    state = radio.setTCXO(1.6);
    if (state != RADIOLIB_ERR_NONE) {
        while (true) {
            Serial.println("Configuration Failed!");
            neopixelWrite(RGB_DATA_PIN, 100, 0, 0); // Red-blue flashes on setup error, blocks initialization
            Serial.print("Error: ");
            Serial.println(state);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            delay(10);
            neopixelWrite(RGB_DATA_PIN, 0, 100, 0);
            delay(200);
        }
    }

    radio.setPacketReceivedAction(setFlag);
    radio.startReceive();
}

volatile long long lastPacketTime = 0;
volatile long long lastError = 0;
volatile long int count;
volatile bool link_down = false;

void loop() {
    if (packetReceived) {
        packetReceived = false;

        int state = radio.readData((uint8_t*)&rxData, sizeof(rxData));

        radio.startReceive();
        if (state == RADIOLIB_ERR_NONE && rxData.identifier == 1) {
            link_down = false;
            float snr = radio.getSNR();
            count = rxData.messageID;

            char json[128];
            snprintf(json, sizeof(json),
            "{\"type\":\"PACKET\",\"ID\":%d,\"data1\":%lu,\"data2\":%lu,\"snr\":%.2f}",
            rxData.messageID,
            rxData.telemetry,
            rxData.telemetry2,
            snr);
            Serial.println(json);

            lastPacketTime = millis();
            neopixelWrite(RGB_DATA_PIN, 0, 50, 0); // Green flashes indicate a complete successful track
            delay(25);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
        } else {
            lastPacketTime = millis();
            neopixelWrite(RGB_DATA_PIN, 50, 0, 0); // Red flash for frame checksum or CRC failure
            delay(25);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            char json[128];
            snprintf(json, sizeof(json),
            "{\"type\":\"DATA_ERR\",\"ID\":%d,\"data1\":%lu,\"data2\":%lu,\"snr\":%.2f}", -1, millis(), 0, 0.00);
            Serial.println(json);
        }
    }

    if (millis() - lastPacketTime >= 2600) {
        if (!link_down){
            link_down = true;
            lastError = millis();
            neopixelWrite(RGB_DATA_PIN, 50, 0, 50); // Steady purple signifies absolute connection loss
            delay(25);
            neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
            char json[128];
            snprintf(json, sizeof(json),
            "{\"type\":\"LINK_ERR\",\"ID\":%d,\"data1\":%lu,\"data2\":%lu,\"snr\":%.2f}", -2, millis(), 0, 0.00);
            Serial.println(json);
        } else {
            if (millis() - lastError >= 2500){
                lastError = millis();
                neopixelWrite(RGB_DATA_PIN, 50, 0, 50); // Steady purple signifies absolute connection loss
                delay(25);
                neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
                char json[128];
                snprintf(json, sizeof(json),
                "{\"type\":\"LINK_ERR\",\"ID\":%d,\"data1\":%lu,\"data2\":%lu,\"snr\":%.2f}", -2, millis(), 0, 0.00);
                Serial.println(json);
            }          
        }   
    }
}