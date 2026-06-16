#include <Arduino.h>

uint32_t getReading(){
    return (uint32_t)touchRead(1);
}

uint32_t getReading2(){
    return (uint32_t)touchRead(2);
}