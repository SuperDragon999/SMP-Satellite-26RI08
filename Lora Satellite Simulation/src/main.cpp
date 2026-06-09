#include <Arduino.h>
#include <RadioLib.h>
#include <TinyGPS++.h>
#include <XPowersLib.h>

struct __attribute__((packed)) TelemetryPacket {
    uint32_t packetId;
    float latitude;
    float longitude;
    float altitude;
    uint8_t satellites;
    int16_t txPower;
};

SX1278 radio = new Module(18, 26, 23, 33);
TinyGPSPlus gps;
HardwareSerial gpsSerial(1);
XPowersAXP2101 powerManager;

uint32_t msgCounter = 0;

void initPowerManagement() {
    Wire.begin(21, 22);
    if (!powerManager.begin(Wire, AXP2101_SLAVE_ADDRESS, 21, 22)) {
        Serial.println("Failed to initialize PMIC!");
        while (1);
    }
    
    powerManager.setALDO2Voltage(3100); 
    powerManager.enableALDO2();
    
    powerManager.setBLDO1Voltage(3300); 
    powerManager.enableBLDO1();
}

void setup() {
    Serial.begin(115200);
    while (!Serial); 
    
    Serial.println(F("\n--- T-BEAM V1.2 STREAMLINED GPS SENDER ---"));
    
    initPowerManagement();
    
    gpsSerial.begin(9600, SERIAL_8N1, 34, 12);
    
    Serial.print(F("[SX1278] Initializing RadioLib ... "));
    int state = radio.begin(433.0, 125.0, 9, 7, RADIOLIB_SX127X_SYNC_WORD, 17, 8, 0);
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("success!"));
    } else {
        Serial.print(F("failed, code "));
        Serial.println(state);
        while (1);
    }
    
    Serial.println(F("System active. Waiting for outdoor satellite fix to begin transmitting..."));
    Serial.println(F("-------------------------------------------------------------------------"));
}

void loop() {
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }

    static uint32_t lastTxTime = 0;
    if (millis() - lastTxTime > 5000) { 
        lastTxTime = millis();

        if (gps.location.isValid()) {
            TelemetryPacket packet;
            packet.packetId = msgCounter++;
            packet.latitude = (float)gps.location.lat();
            packet.longitude = (float)gps.location.lng();
            packet.altitude = (float)gps.altitude.meters();
            packet.satellites = (uint8_t)gps.satellites.value();
            packet.txPower = 17; 

            Serial.printf("[GPS FIX ACCQUIRED] Lat: %.6f | Lng: %.6f | Sats: %d\n", 
                          packet.latitude, packet.longitude, packet.satellites);
            
            Serial.print(F("[SX1278] Transmitting LoRa Packet... "));
            int state = radio.transmit((uint8_t*)&packet, sizeof(TelemetryPacket));

            if (state == RADIOLIB_ERR_NONE) {
                Serial.println(F("SUCCESS!"));
            } else {
                Serial.printf("FAILED (RadioLib Code: %d)\n", state);
            }
        } else {
            Serial.printf("[STATUS] Searching for sky... Satellites in view: %d\n", gps.satellites.value());
        }
    }
}