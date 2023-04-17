# Class instantiation
dsdr = Dosador(
    utils.getContent('id'), # ID
    -3,                     # UTC
    33,                     # releaseButton
    14,                     # wlanLed
    12,                     # releaseLed
    22,                     # scaleD
    23                      # scaleSCK
)

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

# Monitor de agendamentos
async def monitorSchedules(equipment):
    while True:
        await uasyncio.sleep(30)
        thisMinute = equipment.getCurrentMinute()
        # print(f'Starting check for minute {thisMinute}')
        if equipment.lastMinChecked != thisMinute or equipment.lastMinChecked == -1:
            print("Different minute, updating schedules")
            equipment.lastMinChecked = thisMinute
            await equipment.updateSchedules()
            schedule = await equipment.checkSchedules()

            if schedule:
                dOUT12.on()
                print(f'Schedule found, releasing {schedule["qtt"]} grams')
                # equipment.releaseFood(schedule["qtt"])
            else:
                print("No schedules for this minute")

        else:
            print("Minute already checked, skipping...")

# Monitor de pesagem da balança
async def monitorWeight(equipment):

    # Apenas para facilitar testes, após isso o tare deverá ser definido através de botão físico
    equipment.tare = await equipment.getCurrentWeight()


    while True:
        weight = await equipment.checkWeightChange()
        if weight >= 0:
            await equipment.sendNewWeight()
            print("Peso alterado: ", weight)
        else:
            print("Peso permaneceu.", equipment.lastWeight)
        print("Lista de pesos", equipment.weightList)
        await uasyncio.sleep(1)

async def storeDatetime(equipment):
    while True:
        await uasyncio.sleep(60)
        utils.storeContent("datetime.json", json.dumps(equipment.getDatetime()))

# Loop padrão
async def main(loopingLed):
    while True:
        loopingLed.value(not loopingLed.value())
        try:
            print(dsdr.getReadableTime(), "     Temp: ", utils.getTemperature(), "ºC")
        except Exception as e:
            print(e)
        await uasyncio.sleep(1)



loop = uasyncio.get_event_loop()
loop.create_task(main(dOUT13))
loop.create_task(monitorWlan(dsdr))
loop.create_task(monitorReleaseBtn(dsdr))
loop.create_task(monitorWeight(dsdr))
loop.create_task(monitorSchedules(dsdr))
loop.create_task(storeDatetime(dsdr))
loop.run_forever()