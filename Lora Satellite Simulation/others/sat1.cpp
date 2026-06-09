//SAT-1 IS ALWAYS THE ONE RECEIVING SIGNALS AND RESPONDING TO THE PING
#include <SPI.h>
#include <RadioLib.h>
#define XPOWERS_CHIP_AXP2101
#include <XPowersLib.h> // Required for powering the LoRa chip
#include "touch_sensor.h"

#define CURRENT_SAT_ID 2

// T-Beam V1.2 LoRa Pin Definitions
#define LORA_SCK   5
#define LORA_MISO  19
#define LORA_MOSI  27
#define LORA_SS    18
#define LORA_RST   23
#define LORA_DIO0  26

#define LORA_FREQ 433.0
#define SYNC_WORD 0x12

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

SatellitePayload rxData;
SatellitePayload txData;

// Volatile flag for interrupt handling
volatile bool receivedFlag = false;

// ISR executed when a packet is received
#if defined(ESP32) || defined(ESP8266)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
    receivedFlag = true;
}

void initPMU() {
    if (!PMU.begin(Wire, AXP2101_SLAVE_ADDRESS, 21, 22)) {
        Serial.println("Failed to find AXP2101 PMU");
        while (1) delay(1000);
    }
    
    // ALDO2 powers the LoRa radio chip on T-Beam V1.2
    PMU.setALDO2Voltage(3300); // 3.3V
    PMU.enableALDO2();
    
    Serial.println("AXP2101 PMU initialized, LoRa powered on.");
}

void setup() {
    Serial.begin(921600);
    delay(1000); // Let serial stabilize

    // 1. Initialize Power Management Chip first!
    Wire.begin(21, 22);
    initPMU();

    // 2. Setup SPI interface
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);

    // 3. Initialize LoRa Radio
    Serial.print("Initializing Radio... ");
    int state = radio.begin(
        LORA_FREQ,
        125.0,      // Bandwidth
        7,          // Spreading Factor
        5,          // Coding Rate
        SYNC_WORD,
        17,         // Output power (dBm)
        8,          // Preamble length
        0           // Gain
    );

    if (state != RADIOLIB_ERR_NONE) {
        Serial.print("failed, code: ");
        Serial.println(state);
        while (true) delay(1000);
    }
    Serial.println("success!");

    // 4. Setup interrupt callback for packet arrivals
    radio.setDio0Action(setFlag, RISING);

    Serial.println("SAT2 ready, starting listening mode...");
    radio.startReceive();
}

void loop() {
    if (receivedFlag) {
        receivedFlag = false;

        // 1. Read incoming 13-byte data packet
        int state = radio.readData((uint8_t*)&rxData, sizeof(rxData));

        if (state == RADIOLIB_ERR_NONE) {
            if (rxData.sourceNodeId != CURRENT_SAT_ID) {
                
                // 2. IMMEDIATE LINK-LAYER ACK (1 byte)
                uint8_t ackByte = 0xAC; 
                radio.transmit(&ackByte, 1); 

                // 3. PREPARE & SEND APPLICATION RESPONSE (13 bytes)
                txData.sourceNodeId = CURRENT_SAT_ID;
                txData.messageId = rxData.messageId;
                txData.status = 123; // Your data
                txData.commandId = (rxData.commandId == 1) ? 2 : 0;

                // Brief window to let Node 1 settle back into RX mode
                delay(5); 
                
                radio.transmit((uint8_t*)&txData, sizeof(txData));
                
                Serial.println("Data RX -> ACK sent -> App Response sent.");
            }
        }
        
        // Return to listening mode
        radio.startReceive();
    }
}