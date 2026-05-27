#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include "touch_sensor.h"

#define RGB_DATA_PIN 38
#define RGB_PWR_PIN 39

#define CURRENT_SAT_ID 1

uint8_t satellite2Mac[] = {0x80, 0xB5, 0x4E, 0xEA, 0x4F, 0x88}; 

struct SatellitePayload {
    uint8_t sourceNodeId; 
    uint32_t messageId;   
    uint32_t status;      
    uint32_t commandId;   
};

SatellitePayload txData;
SatellitePayload rxData;
esp_now_peer_info_t peerInfo;

volatile bool rxFlag = false;
volatile bool txFlag = false;
volatile esp_now_send_status_t replyStatus;

void OnDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
    if (len == sizeof(SatellitePayload)) {
        memcpy(&rxData, incomingData, sizeof(SatellitePayload));
        if (rxData.sourceNodeId != CURRENT_SAT_ID) {
            rxFlag = true;
        }
    }
}

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    replyStatus = status;
    txFlag = true;
}

void setup() {
    pinMode(RGB_PWR_PIN, OUTPUT);
    digitalWrite(RGB_PWR_PIN, HIGH);
    neopixelWrite(RGB_DATA_PIN, 20, 0, 20);

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    
    esp_wifi_start(); 
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE); 
    esp_wifi_set_promiscuous(false);

    if (esp_now_init() != ESP_OK) return;

    esp_now_register_recv_cb(OnDataRecv);
    esp_now_register_send_cb(OnDataSent);
    
    memset(&peerInfo, 0, sizeof(peerInfo));
    memcpy(peerInfo.peer_addr, satellite2Mac, 6);
    peerInfo.channel = 1;  
    peerInfo.encrypt = false;
    esp_now_add_peer(&peerInfo);
    
    neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
}
 
void loop() {
    if (rxFlag) {
        rxFlag = false;
        
        neopixelWrite(RGB_DATA_PIN, 0, 0, 30);
        delay(60); 
        
        txData.sourceNodeId = CURRENT_SAT_ID;
        txData.messageId = rxData.messageId; 
        txData.status = (uint32_t)getReading(); 
        
        if (rxData.commandId == 1) {
            txData.commandId = 2; 
        } else {
            txData.commandId = 0; 
        }
        
        esp_now_send(satellite2Mac, (uint8_t *) &txData, sizeof(txData));
        
        unsigned long startWait = millis();
        while (!txFlag && (millis() - startWait < 100)) {
            delay(1);
        }
        
        if (txFlag) {
            txFlag = false;
            if (replyStatus == ESP_NOW_SEND_SUCCESS) {
                neopixelWrite(RGB_DATA_PIN, 0, 30, 0);
            } else {
                neopixelWrite(RGB_DATA_PIN, 30, 0, 0);
            }
        }
        
        delay(200);
        neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
    }
    delay(10);
}