wlanCheck = utils.getContent("wlan.json")

if( not wlanCheck or wlanCheck == ''):
    print("Starting in SETUP mode")

    print("=================================================")
    print("=================================================")
    print("=================================================")

    ap = network.WLAN(network.AP_IF)

    ap.config(essid="Monitor Pet", authmode=0, dhcp_hostname="MonitorPet")
    ap.ifconfig(('1.1.1.1', '255.255.255.0', '1.1.1.100', '8.8.8.8'))

    ap.active(True)

    while not ap.active():
        pass

    print('Connection successful')

    print(ap.ifconfig())

    def web_page():
        f = open('setup.html')
        html = f.read()
        f.close()
        return html

    def is_json(myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        # print('Content = %s' % str(request))

        decodedRqst = request.decode('utf-8')
        rqst = decodedRqst.split("\r\n")

        method = rqst[0]
        if "POST" in method:
            for i in range(0, len(rqst)):
                if(is_json(rqst[i])):
                    print(rqst[i])
                    utils.storeContent('wlan.json', rqst[i])
                    time.sleep(2)
                    conn.send("0")
                    machine.reset()
        else:
            response = web_page()
            conn.send(response)

        conn.close()

else:
    print("Starting in REGULAR mode")
    
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
    async def monitorSetupBtn(equipment):
        while True:
            if equipment.tareBtn.value() == 0:
                await uasyncio.sleep(2)
                if equipment.tareBtn.value() == 0:

                    for _ in range(4):
                        equipment.wlanLed.value(not equipment.wlanLed.value())
                        time.sleep(1)

                    if equipment.tareBtn.value() == 0:
                        await equipment.resetWlan()
                    else:
                        await equipment.tareAction()
            await uasyncio.sleep_ms(300)

    # Monitor de agendamentos
    async def monitorSchedules(equipment):
        while True:
            await uasyncio.sleep(30)
            thisMinute = equipment.getCurrentMinute()
            if equipment.lastMinChecked != thisMinute or equipment.lastMinChecked == -1:

                # print("Different minute, updating schedules")

                equipment.lastMinChecked = thisMinute

                await equipment.updateSchedules()

                schedule = await equipment.checkSchedules()

                if schedule:
                    # print(f'Schedule found, releasing {schedule["qtt"]} grams')
                    await equipment.releaseFood(schedule["qtt"])

            # else:
            #     print("Minute already checked, skipping...")

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

    # Imprime informações para debug no console
    async def debugLoop():
        while True:
            try:
                print("#", dsdr.getReadableTime(), utils.getTemperature(), "ºC", dsdr.lastWeight, dsdr.weightList)
            except Exception as e:
                print(e)
            await uasyncio.sleep(60)

    async def clockLed():
        loopingLed  = Pin(2,  Pin.OUT, drive=Pin.DRIVE_0)
        while True:
            loopingLed.value(not loopingLed.value())
            await uasyncio.sleep(1)


    loop = uasyncio.get_event_loop()
    loop.create_task(clockLed())
    loop.create_task(debugLoop())
    loop.create_task(monitorWlan(dsdr))
    loop.create_task(monitorReleaseBtn(dsdr))
    loop.create_task(monitorWeight(dsdr))
    loop.create_task(monitorSchedules(dsdr))
    loop.create_task(storeDatetime(dsdr, 60))
    loop.create_task(monitorSetupBtn(dsdr))
    loop.run_forever()


