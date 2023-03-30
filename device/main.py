# Class instantiation
dsdr = Dosador(
    utils.getContent('id'), # ID
    -3,                     # UTC
    dOUT14,                 # wlanLed
    dIN33,                  # releaseButton
    dOUT12                  # releaseLed
    )

# Interrupts
# dIN33.irq(trigger=Pin.IRQ_RISING, handler=dsdr.releasePressed)

async def monitorWlan(equipment):

    await uasyncio.sleep(2)

    await equipment.wlanconnect()

    while True:
        if not equipment.wlan.isconnected():
            await equipment.wlanAttemptingToConnect()
        await uasyncio.sleep(5)

async def monitorReleaseBtn(equipment):
    while True:
        if equipment.releaseBtn.value() == 0:
            await equipment.releaseAction()
        await uasyncio.sleep_ms(300)
    
async def monitorSchedules(equipment):
    while True:
        # Verificar se este minuto é diferente desde o último loop
        # Se for diferente, atualizar o json
        # Se for diferente, verificar se algum agendamento bate com os cadastrados
        await uasyncio.sleep(30)

async def main():
    while True:
        dOUT13.value(not dOUT13.value())
        print(dsdr.getReadableTime(), "     Temp: ", utils.getTemperature(), "ºC")
        await uasyncio.sleep(1)



loop = uasyncio.get_event_loop()
loop.create_task(main())
loop.create_task(monitorWlan(dsdr))
loop.create_task(monitorReleaseBtn(dsdr))
loop.run_forever()