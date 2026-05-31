#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <ESPAsyncWebServer.h>

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

SatellitePayload txData;
SatellitePayload rxData;
esp_now_peer_info_t peerInfo;

volatile bool txUpdated = false;
volatile esp_now_send_status_t lastTxStatus;
volatile bool rxUpdated = false;

// High-resolution diagnostic metric shared with the web endpoint
volatile unsigned long lastFlightTimeMicros = 0;

AsyncWebServer server(80);
AsyncWebSocket ws("/telemetry");

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    lastTxStatus = status;
    txUpdated = true;
}

void OnDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
    if (len == sizeof(SatellitePayload)) {
        memcpy(&rxData, incomingData, sizeof(SatellitePayload));
        if (rxData.sourceNodeId != CURRENT_SAT_ID) {
            rxUpdated = true;
            String json = "{";
            json += "\"Type\":" + String("\"Packet\"") + ",";
            json += "\"ID\":" + String(rxData.messageId) + ",";
            json += "\"sensor\":" + String(rxData.status) + ",";
            json += "\"latency\":" + String(lastFlightTimeMicros);
            json += "}";
        
            ws.textAll(json);
        }
    }
}

void setup() {
    Serial.begin(115200);

    pinMode(RGB_PWR_PIN, OUTPUT);
    digitalWrite(RGB_PWR_PIN, HIGH);

    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP("Satellite-Ground-Station", ""); 
    
    esp_wifi_start(); 
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE); 
    esp_wifi_set_promiscuous(false);

    if (esp_now_init() != ESP_OK) {
        return;
    }

    ws.onEvent([](AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {});
    server.addHandler(&ws);

    esp_now_register_send_cb(OnDataSent);
    esp_now_register_recv_cb(OnDataRecv);
    
    memset(&peerInfo, 0, sizeof(peerInfo));
    memcpy(peerInfo.peer_addr, satellite1Mac, 6);
    peerInfo.channel = 1;  
    peerInfo.encrypt = false;
    esp_now_add_peer(&peerInfo);

    server.begin();
}

int count = 1;
void loop() {
    if (Serial) {
        Serial.println("[+] Dual ESP-NOW & HTTP Webserver Ground Station Active.");
        Serial.print("[+] Ground Station Gateway IP Address: ");
        Serial.println(WiFi.softAPIP());
    }
    txData.messageId = count;
    txData.sourceNodeId = CURRENT_SAT_ID;
    txData.status = 0; 
    txData.commandId = 1; 
    
    if (Serial) {
        Serial.println("\n[SAT 2] Transmitting PING frame...");
    }
    
    neopixelWrite(RGB_DATA_PIN, 30, 30, 0);
    delay(100);
    
    // Start high-resolution stopwatch right before pushing packet into the RF pipeline
    unsigned long startMicros = micros();
    
    esp_now_send(satellite1Mac, (uint8_t *) &txData, sizeof(txData));
    
    unsigned long startWait = millis();
    while (!txUpdated && (millis() - startWait < 200)) {
    }

    // Capture precise completion timestamp
    unsigned long endMicros = micros();
    lastFlightTimeMicros = endMicros - startMicros;

    if (txUpdated) {
        txUpdated = false;
        if (lastTxStatus == ESP_NOW_SEND_SUCCESS) {
            if (Serial) {
                Serial.printf("[SAT 2 TX] ACK Received! Latency: %lu us\n", lastFlightTimeMicros);
            }
            neopixelWrite(RGB_DATA_PIN, 0, 10, 0); 
        } else {
            if (Serial) {
                Serial.printf("[SAT 2 TX] DROP! Dropped frame: %d\n", count);
                Serial.println("-----------------------------------------\n");
                String json = "{\"Type\": \"ERR\",";
                json += "\"ID\":" + String(count);
                json += "}";
                ws.textAll(json);
            }
            neopixelWrite(RGB_DATA_PIN, 10, 0, 0); 
        }
        count++;
    }

    if (rxUpdated) {
        rxUpdated = false;
        neopixelWrite(RGB_DATA_PIN, 0, 0, 30);
        
        if (Serial) {
            Serial.printf("\n<<< [SAT 2 RX] Received Data From Sat [%d] >>>\n", rxData.sourceNodeId);
            Serial.printf("Telemetry Frame ID: %lu\n", (unsigned long)rxData.messageId); 
            Serial.printf("Sat 1 Touch Capacitance Value: %lu\n", (unsigned long)rxData.status);
            Serial.printf("Response Command ID: %lu\n", (unsigned long)rxData.commandId);
            Serial.println("-----------------------------------------\n");
        }
    }

    neopixelWrite(RGB_DATA_PIN, 0, 0, 0);
    delay(3000);
}