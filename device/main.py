while True:

    if(dIN14.value() == 1):
        dOUT13.on();
    else:
        dOUT13.off();

    time.sleep(1);
