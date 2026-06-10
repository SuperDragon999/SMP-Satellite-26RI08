#include <SPI.h>
#include <RadioLib.h>
#define XPOWERS_CHIP_AXP2101
#include <XPowersLib.h> // Required for powering the LoRa chip

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
    uint8_t sourceNodeId;   // 1 byte
    uint32_t messageId;     // 4 bytes
    uint32_t status;        // 4 bytes
    uint32_t commandId;     // 4 bytes
};                          // Total: 13 bytes

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
            // Ensure we aren't talking to ourselves
            if (rxData.sourceNodeId != CURRENT_SAT_ID) {
                
                // 2. PREPARE COMBINED RESPONSE (Acts as both ACK and Data)
                txData.sourceNodeId = CURRENT_SAT_ID;
                txData.messageId = rxData.messageId; // Proves we received their exact packet
                txData.status = 123;                 // Telemetry data
                txData.commandId = (rxData.commandId == 1) ? 2 : 0;
                
                // Send everything in one single clean burst
                int txState = radio.transmit((uint8_t*)&txData, sizeof(txData));
                
                if (txState == RADIOLIB_ERR_NONE) {
                    Serial.println("Combined ACK & Data Response sent successfully.");
                } else {
                    Serial.print("TX failed, code: ");
                    Serial.println(txState);
                }
            }
        }
        
        // Always make sure the radio drops back into listening mode
        radio.startReceive();
    }
}