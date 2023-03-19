setupWifi(){


    esp_wifi_init(WIFI_INIT_CONFIG_DEFAULT());

    esp_wifi_set_mode(WIFI_MODE_STA);

    esp_wifi_start();

    esp_wifi_connect();


}