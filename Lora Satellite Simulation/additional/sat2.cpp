//SAT-2 IS ALWAYS THE ONE SENDING PINGS
#include <SPI.h>
#include <RadioLib.h>
#define XPOWERS_CHIP_AXP2101
#include <XPowersLib.h> // Required for powering the LoRa chip on T-Beam v1.2
#define LED_PIN 4
#define CURRENT_SAT_ID 2

// T-Beam V1.2 LoRa Pin Definitions
#define LORA_SCK   5
#define LORA_MISO  19
#define LORA_MOSI  27
#define LORA_SS    18
#define LORA_RST   23
#define LORA_DIO0  26

#define LORA_FREQ  433.0
#define SYNC_WORD  0x12

XPowersPMU PMU;

struct SatellitePayload {
    uint8_t sourceNodeId;
    uint32_t messageId;
    uint32_t status;
    uint32_t commandId;
};

SX1278 radio = new Module(
    LORA_SS,
    LORA_DIO0,
    LORA_RST,
    RADIOLIB_NC
);

volatile bool rxUpdated = false;
volatile unsigned long lastLatency = 0;
SatellitePayload txData;
SatellitePayload rxData;

#if defined(ESP32) || defined(ESP8266)
  ICACHE_RAM_ATTR
#endif
void setFlag() {
    rxUpdated = true;
}

void initPMU() {
    if (!PMU.begin(Wire, AXP2101_SLAVE_ADDRESS, 21, 22)) {
        Serial.println("Failed to find AXP2101 PMU");
    }
    
    // Power up the SX1278 Radio
    PMU.setALDO2Voltage(3300); // 3.3V
    PMU.enableALDO2();
}

void setupRadio() {
    int state = radio.begin(
        LORA_FREQ,
        125.0,
        7,
        5,
        SYNC_WORD,
        17,
        8,
        0
    );

    if (state != RADIOLIB_ERR_NONE) {
        Serial.print("RadioLib setup failed, error: ");
        Serial.println(state);
    }

    radio.setDio0Action(setFlag, RISING);
    radio.startReceive();
}

void setup() {
    Serial.begin(921600);

    // Initialize I2C pins for the power management chip
    Wire.begin(21, 22); 
    // Initialize Power Management Chip
    initPMU(); 
    // Initialize SPI for LoRa
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    // Setup RadioLib
    setupRadio();
    pinMode(LED_PIN, OUTPUT);
}

int count = 0;
void loop() {
    unsigned long loopStart = millis();
    txData.sourceNodeId = CURRENT_SAT_ID;
    txData.messageId = count;
    txData.status = 0;
    txData.commandId = 1; // PING

    // Start microsecond level stopwatch to measure link-layer latency
    unsigned long start = micros();

    // 1. Transmit packet (blocking call)
    int txState = radio.transmit((uint8_t*)&txData, sizeof(txData));
    if (txState != RADIOLIB_ERR_NONE) {
        Serial.print("Transmit failed, code: ");
        Serial.println(txState);
    }
    digitalWrite(LED_PIN, HIGH); //Set the LED to High when the message is sent
    
    // 2. CRITICAL: Clear the flag
    rxUpdated = false; 

    // 3. Put radio in receive mode to listen for the echo
    radio.startReceive();

    unsigned long timeout = millis();
    bool replied = false;

    // Wait up to 200ms for a response
    while (millis() - timeout < 200) {
        if (rxUpdated) {
            rxUpdated = false; // Reset flag for next time

            //Check data of the state
            int state = radio.readData((uint8_t*)&rxData, sizeof(rxData));
            if (state == RADIOLIB_ERR_NONE) {
                // Validate it's the response matching our message ID
                if (rxData.commandId == 2 && rxData.messageId == txData.messageId) {
                    lastLatency = micros() - start;
                    replied = true;
                    digitalWrite(LED_PIN, LOW); // Turn LED back to low mode when response has been received

                    //Prepare the message 
                    char json[128];

                    snprintf(json, sizeof(json),
                    "{\"Type\":\"Packet\",\"ID\":%d,\"sensor\":%d,\"latency\":%ld}",
                    rxData.messageId,
                    rxData.status,
                    lastLatency);

                    Serial.println(json);
                    break; 
                }
            } else {
                //ERROR
                char json[64];
                snprintf(json, sizeof(json),
                "{\"Type\":\"ERR\",\"ID\":%d}",
                count);

                Serial.println(json);
            }

            // If it wasn't the packet we wanted, resume listening
            radio.startReceive();
        }
    }

    if (!replied) {
        char json[64];
        snprintf(json, sizeof(json),
        "{\"Type\":\"ERR\",\"ID\":%d}",
        count);

        Serial.println(json);
    }
    count++;
    unsigned long exeTime = millis() - loopStart;
    if (exeTime < 1000) {
        delay(1000 - exeTime);
    }
}