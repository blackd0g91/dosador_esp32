# TODO: Armazenar e buscar id e apiKey de outro local (non-volatile ou arquivo)
dsdr = Dosador('6bfb570b-ff74-417e-aef9-a46ac66c0184', 'e5dd09c6-a4bf-46bf-af56-4c533f5c60aa')

dsdr.wlanconnect(dOUT14)

while True:
    dOUT13.on()
    time.sleep(3)
    dOUT13.off()
    time.sleep(3)
    print("Looping...")
