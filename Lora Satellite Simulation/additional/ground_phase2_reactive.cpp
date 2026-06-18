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

uint8_t currentSF = 12; // CHANGE BEFORE EACH TEST
float currentBW = 500; // CHANGE BEFORE EACH TEST

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

SatellitePayload rxData;
AckPayload ackData;

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
            delay(200);
            neopixelWrite(RGB_DATA_PIN, 0, 100, 0);
            delay(200);
        }
    }

    radio.setPacketReceivedAction(setFlag);
    radio.startReceive();
}

volatile long long loopStart;
void loop() {
    loopStart = millis();
    if (packetReceived) {
        packetReceived = false;

        int state = radio.readData((uint8_t*)&rxData, sizeof(rxData));
        if (state == RADIOLIB_ERR_NONE) {
            float snr = radio.getSNR();

            // uint8_t nextSF = currentSF;
            // uint8_t nextBWCode = 1; 

            // // REDESIGN THIS SYSTEM
            // if (fei > 15000.0) {
            //     nextBWCode = 2; // Expand Bandwidth to 250.0 kHz (Widening the tracking window)
            //     if (snr < -10.0) {
            //         nextSF = 8;
            //     } else {
            //         nextSF = 7; // Optimize for max dynamic Doppler acceleration
            //     }
            // } else if (fei > 5000.0) {
            //     nextBWCode = 1; // Return to standard 125.0 kHz Bandwidth
            //     if (snr < -15.0) {
            //         nextSF = 10;
            //     } else if (snr < -10.0) {
            //         nextSF = 9;
            //     } else {
            //         nextSF = 8;
            //     }
            // } else {
            //     nextBWCode = 0; // Compress down to 62.5 kHz to maximize processing gain at deep horizons
            //     if (snr < -15.0) {
            //         nextSF = 11; // Maximum sensitivity target within the defined scope
            //     } else {
            //         nextSF = 9;
            //     }
            // }

            // ackData.packetType = 2; 
            // ackData.identifier = ID; 
            // ackData.messageId = rxData.messageId; 
            // ackData.targetSF = nextSF;
            // ackData.targetBWCode = nextBWCode;
            
            // // Short turnaround delay to let the satellite state machine flip to RX mode
            // delay(10);
            
            // // Send acknowledgement link frames using the CURRENT tracking settings
            // radio.transmit((uint8_t*)&ackData, sizeof(ackData));
            // neopixelWrite(RGB_DATA_PIN, 0, 0, 30); // Blue flash confirms uplink tracking acknowledgement
            
            // // Reconfigure the system properties for the incoming packet window
            // currentSF = nextSF;
            // if (nextBWCode == 0) currentBW = 62.5;
            // else if (nextBWCode == 1) currentBW = 125.0;
            // else if (nextBWCode == 2) currentBW = 250.0;
            
            // radio.standby();
            // radio.setBandwidth(currentBW);
            // radio.setSpreadingFactor(currentSF);
            char json[128];
            snprintf(json, sizeof(json),
            "{\"type\":\"telemetry\",\"id\":%d,\"tel\":%lu,\"sf\":%d,\"bw\":%.1f,\"snr\":%.2f}",
            rxData.messageId,
            rxData.telemetry,
            currentSF,
            currentBW,
            snr);

            Serial.println(json);
            neopixelWrite(RGB_DATA_PIN, 0, 50, 0); // Green flashes indicate a complete successful tracking swap
        } else {
            neopixelWrite(RGB_DATA_PIN, 50, 0, 0); // Red flash for frame checksum or CRC failure
            char json[128];
            snprintf(json, sizeof(json),"{\"type\":\"DATA_ERR\"}");
            Serial.println(json);
        }
        
        radio.startReceive();
    }
}