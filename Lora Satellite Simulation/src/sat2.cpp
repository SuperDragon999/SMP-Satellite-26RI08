//SAT-2 IS ALWAYS THE ONE SENDING PINGS
#include <SPI.h>
#include <RadioLib.h>
#define XPOWERS_CHIP_AXP2101
#include <XPowersLib.h> // Required for powering the LoRa chip on T-Beam v1.2

#define CURRENT_SAT_ID 1

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

volatile bool receivedFlag = false;

#if defined(ESP32) || defined(ESP8266)
  ICACHE_RAM_ATTR
#endif
void setFlag() {
    receivedFlag = true;
}

void initPMU() {
    if (!PMU.begin(Wire, AXP2101_SLAVE_ADDRESS, 21, 22)) {
        Serial.println("Failed to find AXP2101 PMU");
        while (1) delay(1000);
    }
    
    // Power up the SX1278 Radio
    PMU.setALDO2Voltage(3300); // 3.3V
    PMU.enableALDO2();
    Serial.println("AXP2101 PMU Ready - LoRa Powered On");
}

void setupRadio() {
    Serial.print("Initializing Radio... ");
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
        Serial.print("failed, code: ");
        Serial.println(state);
        while (true) delay(1000);
    }
    Serial.println("success!");

    radio.setDio0Action(setFlag, RISING);
    radio.startReceive();
}

SatellitePayload txData;
SatellitePayload rxData;
int count = 0;

void setup() {
    Serial.begin(921600);

    Serial.println("System starting...");

    // Initialize I2C pins for the power management chip
    Wire.begin(21, 22); 
    Serial.println("I2C bus initialized.");

    // Initialize Power Management Chip
    initPMU(); 
    Serial.println("PMU configured.");

    // Initialize SPI for LoRa
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    Serial.println("SPI bus initialized.");

    // Setup RadioLib
    setupRadio();
    Serial.println("Radio interface ready.");
}

void loop() {
    txData.sourceNodeId = CURRENT_SAT_ID;
    txData.messageId = count;
    txData.status = 0;
    txData.commandId = 1; // PING

    Serial.print("Sending PING #");
    Serial.println(count);

    unsigned long start = micros();

    // 1. Transmit packet (blocking call)
    int txState = radio.transmit((uint8_t*)&txData, sizeof(txData));
    if (txState != RADIOLIB_ERR_NONE) {
        Serial.print("Transmit failed, code: ");
        Serial.println(txState);
    }

    // 2. CRITICAL: Clear the flag because transmit just tripped DIO0 high!
    receivedFlag = false; 

    // 3. Put radio in receive mode to listen for the echo
    radio.startReceive();

    unsigned long timeout = millis();
    bool replied = false;

    // Wait up to 150ms for a response
    while (millis() - timeout < 150) {
        if (receivedFlag) {
            receivedFlag = false; // Reset flag for next time

            int state = radio.readData((uint8_t*)&rxData, sizeof(rxData));

            if (state == RADIOLIB_ERR_NONE) {
                // Validate it's the response matching our message ID
                if (rxData.commandId == 2 && rxData.messageId == txData.messageId) {
                    unsigned long latency = micros() - start;
                    Serial.print("-> ACK RECEIVED! Round-trip Latency: ");
                    Serial.print(latency);
                    Serial.println(" us");
                    replied = true;
                    break; 
                }
            } else {
                Serial.print("Read error during window: ");
                Serial.println(state);
            }

            // If it wasn't the packet we wanted, resume listening
            radio.startReceive();
        }
    }

    if (!replied) {
        Serial.println("-> TIMEOUT: No response from SAT2");
    }

    count++;
    delay(1000); // Wait 1 second before next ping
}