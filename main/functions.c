void startup_blink(){
    int i;
    for (i = 0; i < 5; i++)
    {
        gpio_set_level(GPIO_NUM_2, 1);
        vTaskDelay(10);
        gpio_set_level(GPIO_NUM_2, 0);
        vTaskDelay(10);
    }
    
}