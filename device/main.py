# Class instantiation
dsdr = Dosador(
    utils.getContent('id'), # ID
    -3,                     # UTC
    32,                     # tareButton
    33,                     # releaseButton
    27,                     # wlanLed
    13,                     # tareLed
    12,                     # releaseLed
    22,                     # scaleD
    23                      # scaleSCK
)

print("=================================================")
print("=================================================")
print("=================================================")

# Gerenciamento da conexão
async def monitorWlan(equipment):

    await uasyncio.sleep(2)

    await equipment.wlanconnect()

    while True:
        if not equipment.wlan.isconnected():
            await equipment.wlanAttemptingToConnect()
        await uasyncio.sleep(5)

# Monitor para o botão de liberar ração
async def monitorReleaseBtn(equipment):
    while True:
        if equipment.releaseBtn.value() == 0:
            await equipment.releaseAction()
        await uasyncio.sleep_ms(300)

# Monitor para o botão de tara
async def monitorTareBtn(equipment):
    while True:
        if equipment.tareBtn.value() == 0:
            await uasyncio.sleep(1)
            if equipment.tareBtn.value() == 0:
                await equipment.tareAction()
        await uasyncio.sleep_ms(300)

# Monitor de agendamentos
async def monitorSchedules(equipment):
    while True:
        await uasyncio.sleep(30)
        thisMinute = equipment.getCurrentMinute()
        if equipment.lastMinChecked != thisMinute or equipment.lastMinChecked == -1:

            print("Different minute, updating schedules")

            equipment.lastMinChecked = thisMinute

            await equipment.updateSchedules()

            schedule = await equipment.checkSchedules()

            if schedule:
                print(f'Schedule found, releasing {schedule["qtt"]} grams')
                await equipment.releaseFood(schedule["qtt"])

        else:
            print("Minute already checked, skipping...")

# Monitor de pesagem da balança
async def monitorWeight(equipment):

    if not equipment.tare:
        await equipment.setTare()

    while True:
        await equipment.checkWeightChange()
        await uasyncio.sleep(1)

# Armazena o horário atual em arquivo, para retomar em caso de queda de energia
async def storeDatetime(equipment, seconds):
    while True:
        await uasyncio.sleep(seconds)
        utils.storeContent("datetime.json", json.dumps(equipment.getDatetime()))

# Loop padrão
async def main():

    loopingLed  = Pin(2,  Pin.OUT, drive=Pin.DRIVE_0)

    while True:
        loopingLed.value(not loopingLed.value())
        try:
            print("#", dsdr.getReadableTime(), utils.getTemperature(), "ºC", dsdr.lastWeight, dsdr.weightList)
        except Exception as e:
            print(e)
        await uasyncio.sleep(1)


loop = uasyncio.get_event_loop()
loop.create_task(main())
loop.create_task(monitorWlan(dsdr))
loop.create_task(monitorReleaseBtn(dsdr))
loop.create_task(monitorWeight(dsdr))
loop.create_task(monitorSchedules(dsdr))
loop.create_task(storeDatetime(dsdr, 60))
loop.create_task(monitorTareBtn(dsdr))
loop.run_forever()