# TODO: Armazenar e buscar id e apiKey de outro local (non-volatile ou arquivo)
dosador = Dosador('6bfb570b-ff74-417e-aef9-a46ac66c0184', 'e5dd09c6-a4bf-46bf-af56-4c533f5c60aa')

# TODO: Armazenar e buscar SSID e Password de outro local (non-volatile ou arquivo)
# TODO: Adicionar LED indicando estado da conexão
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSID", "password")
while not wlan.isconnected():
    print("Connecting...")
    time.sleep(1);
print("Connected")


while True:

    if(dIN33.value() == 1):
        dOUT13.off();
    else:
        dOUT13.on();
        dosador.getSchedules();

    print(dosador.getTemperature())

    time.sleep(1);
