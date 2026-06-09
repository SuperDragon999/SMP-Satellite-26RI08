#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

#define RGB_DATA_PIN 38
#define RGB_PWR_PIN 39
#define CURRENT_SAT_ID 2

uint8_t satellite1Mac[] = {0xDC, 0xB4, 0xD9, 0x0C, 0x68, 0x68}; 

struct SatellitePayload {
    uint8_t sourceNodeId; 
    uint32_t messageId;   
    uint32_t status;      
    uint32_t commandId;   
};

SatellitePayload txData; //txData means data sent from the satellite
SatellitePayload rxData; //rxData means data received from other satellies
esp_now_peer_info_t peerInfo;

//volatile bools (because they constantly change)
volatile bool txUpdated = false; //check if "data sent" status has changed
volatile esp_now_send_status_t lastTxStatus;
volatile bool rxUpdated = false; //check if new data has been received
volatile unsigned long endMicros;

// High-resolution diagnostic metric shared with the web endpoint
volatile unsigned long lastLatency = 0;

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    endMicros = micros();
    lastTxStatus = status;
    txUpdated = true;
}

void OnDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
    if (len == sizeof(SatellitePayload)) {
        memcpy(&rxData, incomingData, sizeof(SatellitePayload));
        if (rxData.commandId == 2 && rxData.sourceNodeId != CURRENT_SAT_ID){ //Ping response (ID = 2), valid packet
            rxUpdated = true; //new packet received
            // String json = "{";
            // json += "\"Type\":" + String("\"Packet\"") + ",";
            // json += "\"ID\":" + String(rxData.messageId) + ",";
            // json += "\"sensor\":" + String(rxData.status) + ",";
            // json += "\"latency\":" + String(lastLatency);
            // json += "}";
            // Serial.println(json);
        }
    }
}

void setup() {
    Serial.begin(912600);

    pinMode(RGB_PWR_PIN, OUTPUT);
    digitalWrite(RGB_PWR_PIN, HIGH);

    WiFi.mode(WIFI_STA);

    esp_wifi_start(); 
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE); 
    esp_wifi_set_promiscuous(false);

    if (esp_now_init() != ESP_OK) {
        return;
    }

    esp_now_register_send_cb(OnDataSent);
    esp_now_register_recv_cb(OnDataRecv);
    
    memset(&peerInfo, 0, sizeof(peerInfo));
    memcpy(peerInfo.peer_addr, satellite1Mac, 6);
    peerInfo.channel = 1;  
    peerInfo.encrypt = false;
    esp_now_add_peer(&peerInfo);
}

int count = 1;
void loop() {
    unsigned long loopStart = millis();
    txData.messageId = count;
    txData.sourceNodeId = CURRENT_SAT_ID;
    txData.status = 0; 
    txData.commandId = 1; 

    txUpdated = false;
    rxUpdated = false;
    neopixelWrite(RGB_DATA_PIN, 38, 14, 46); //Pink light for 80ms for every packet sent
    delay(80);
    
    // Start high-resolution stopwatch right before pushing packet into the RF pipeline
    unsigned long startMicros = micros();
    
    //Send message
    esp_now_send(satellite1Mac, (uint8_t *) &txData, sizeof(txData));
    while(!txUpdated){
        yield();
    }

    lastLatency = endMicros - startMicros;

    if (txUpdated) {
        txUpdated = false;
        if (lastTxStatus == ESP_NOW_SEND_SUCCESS) {
            //Wait for response
            unsigned long rxTimeout = millis();
            while (!rxUpdated && (millis() - rxTimeout < 150)) {
                yield();
            }
            if (rxUpdated) {
                //Received message from SAT 1, print the message (change to JSON packet) to Serial
                rxUpdated = false;
                neopixelWrite(RGB_DATA_PIN, 0, 15, 0); //Green light for every packet received
                char json[128];

                snprintf(json, sizeof(json),
                "{\"Type\":\"Packet\",\"ID\":%d,\"sensor\":%d,\"latency\":%ld}",
                rxData.messageId,
                rxData.status,
                lastLatency);

                Serial.println(json);
            } else {
                //ACK Received, but packet got corrupted on the way back
                char json[64];
                snprintf(json, sizeof(json),
                "{\"Type\":\"ERR\",\"ID\":%d}",
                count);

                Serial.println(json);
                neopixelWrite(RGB_DATA_PIN, 15, 0, 0); //Red light for every error           
            }
        } else {
            //lastTxStatus did not succeed as there is no ACK, send an error JSON message
            char json[64];
            snprintf(json, sizeof(json),
            "{\"Type\":\"ERR\",\"ID\":%d}",
            count);

            Serial.println(json);
            neopixelWrite(RGB_DATA_PIN, 15, 0, 0); //Red light for every error  
        }
        count++; //Increase packet count
    }

    unsigned long exeTime = millis() - loopStart;
    if (exeTime < 1000) {
        delay(1000 - exeTime);
    }
}