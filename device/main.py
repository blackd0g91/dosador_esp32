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
        await uasyncio.sleep(30)
        thisMinute = equipment.getCurrentMinute()
        if equipment.lastMinChecked != thisMinute or equipment.lastMinChecked == -1:
            print("Different minute, updating schedules")
            equipment.lastMinChecked = thisMinute
            await equipment.updateSchedules()
            schedule = await equipment.checkSchedules()

            if schedule:
                equipment.releaseFood(schedule.qtt)

        else:
            print("Skipping schedules update")
        
async def monitorWeight(equipment):
    while True:
        uasyncio.sleep(10)

async def main(loopingLed):
    while True:
        loopingLed.value(not loopingLed.value())
        print(dsdr.getReadableTime(), "     Temp: ", utils.getTemperature(), "ºC")
        await uasyncio.sleep(1)



loop = uasyncio.get_event_loop()
loop.create_task(main(dOUT13))
loop.create_task(monitorWlan(dsdr))
loop.create_task(monitorReleaseBtn(dsdr))
loop.create_task(monitorWeight(dsdr))
loop.run_forever()