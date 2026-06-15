#include <Arduino.h>

uint32_t getReading(){
    return (uint32_t)touchRead(6);
}