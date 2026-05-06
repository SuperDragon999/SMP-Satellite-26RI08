#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsServer.h>
#define RGB_DATA_PIN 38
#define RGB_PWR_PIN 39

const char* ssid = "Golden1234";
const char* password = "chmtebbgnr";

WebSocketsServer webSocket = WebSocketsServer(81);

void setup() {
  Serial.begin(115200);
  while(!Serial) delay(10);

  // Power up the LED rail
  pinMode(RGB_PWR_PIN, OUTPUT);
  digitalWrite(RGB_PWR_PIN, LOW);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  webSocket.begin();
}

void loop() {
  // Print the IP address so you know where to point your Python script
  webSocket.loop();

  static unsigned long lastTime = 0;
  if (millis() - lastTime > 1000) {
    lastTime = millis();
    // This sends the message to all connected clients (your Python frontend)
    webSocket.broadcastTXT("Hello from ESP32!");
    Serial.println("Status: Transmitting...");
    neopixelWrite(RGB_DATA_PIN, 0, 5, 0); //green light to show status
  }
}