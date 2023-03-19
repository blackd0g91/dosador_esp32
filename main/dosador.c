#include <stdio.h>
#include "esp_wifi.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "functions.c"
#include "main.c"
#include "setup.c"

// Led embutido está no GPIO 2

void app_main(void){
    setup();
    while(true) mainLoop();
}