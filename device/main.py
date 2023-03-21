# TODO: Armazenar e buscar id e apiKey de outro local (non-volatile ou arquivo)
dsdr = Dosador('6bfb570b-ff74-417e-aef9-a46ac66c0184', 'e5dd09c6-a4bf-46bf-af56-4c533f5c60aa')

dsdr.wlanconnect(dOUT14)

schedules = dsdr.getSchedules()
print(schedules)

while True:
    dOUT13.value(not dOUT13.value())
    time.sleep(5)
    print("Looping...")
