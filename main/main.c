void mainLoop(){

    printf("looping\n");

    if(gpio_get_level(GPIO_NUM_22)){
        gpio_set_level(GPIO_NUM_26, 0);
    } else {
        gpio_set_level(GPIO_NUM_26, 1);
    }

    vTaskDelay(100);
}