#include <Arduino.h>
#include <RadioLib.h>

#define XPOWERS_CHIP_AXP192
#include <XPowersLib.h>

XPowersPMU PMU;

#define LORA_SCK   5
#define LORA_MISO  19
#define LORA_MOSI  27
#define LORA_CS    18
#define LORA_RST   23
#define LORA_DIO0  26
#define LORA_DIO1  33

SX1278 radio = new Module(LORA_CS, LORA_DIO0, LORA_RST, LORA_DIO1);

void initPowerManagement() {
    Wire.begin(21, 22); 
    
    if (!PMU.begin(Wire, AXP192_SLAVE_ADDRESS, 21, 22)) {
        Serial.println("Failed to find AXP192 Power Management Unit!");
        while (1);
    }

    PMU.setDCDC1Voltage(3300);

    PMU.setLDO2Voltage(3300); 
    PMU.enableLDO2();         

    PMU.setLDO3Voltage(3300); 
    PMU.enableLDO3();         

    Serial.println("AXP192 PMU initialized. LoRa power rail is active.");
}

void setup() {
    Serial.begin(115200);
    while (!Serial);

    initPowerManagement();

    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);

    Serial.print("Initializing LoRa transceiver... ");
    
    float frequency = 433.0;    
    float bandwidth = 125.0;    
    uint8_t spreadingFactor = 9; 
    uint8_t codingRate = 7;     
    uint8_t syncWord = 0x12;    
    int8_t power = 17;          

    int state = radio.begin(frequency, bandwidth, spreadingFactor, codingRate, syncWord, power);

    if (state == RADIOLIB_ERR_NONE) {
        Serial.println("Success!");
    } else {
        Serial.print("Failed with state code: ");
        Serial.println(state);
        while (1);
    }
}

int packetCounter = 0;

void loop() {
    Serial.print("Transmitting telemetry packet [");
    Serial.print(packetCounter);
    Serial.println("]...");

    String message = "Telemetry Packet #" + String(packetCounter);

    int state = radio.transmit(message.c_str());

    if (state == RADIOLIB_ERR_NONE) {
        Serial.println("Transmission completed successfully!");
        Serial.print("Data rate achieved: ");
        Serial.print(radio.getDataRate());
        Serial.println(" bps");
    } else if (state == RADIOLIB_ERR_TX_TIMEOUT) {
        Serial.println("Timeout occurred during transmission!");
    } else {
        Serial.print("Transmission failed, error code: ");
        Serial.println(state);
    }

    packetCounter++;
    delay(5000); 
}