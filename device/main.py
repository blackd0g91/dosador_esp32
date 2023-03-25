while True:

    # Monitorar conexão
    # TODO: Verificar possibilidade de tornar a verificação async
    if not dsdr.wlan.isconnected():
        dOUT14.value(not dOUT14.value())
    else:
        dOUT14.off()

    dOUT13.value(not dOUT13.value())
    time.sleep(1)

    print(dsdr.getReadableTime(), "     Temp: ", utils.getTemperature(), "ºC")

    if(dIN33.value() == 0):
        rqst = dsdr.getSchedules()
        print(rqst)
        while dIN33.value == 1:
            time.sleep_ms(100)