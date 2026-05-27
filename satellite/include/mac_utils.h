#include "WiFi.h"

//Find ESP-32 STA MAC address
void printSystemMacAddresses() {
    WiFi.mode(WIFI_MODE_STA);
    Serial.println(WiFi.macAddress());
    delay(5000);
}