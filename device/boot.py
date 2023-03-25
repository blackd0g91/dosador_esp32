# This file is executed on every boot (including wake-boot from deepsleep)
import time
import ntptime
import network
import json
from machine import Pin
import dosador
from dosador import Dosador
import utils
import uasyncio

# Digital Inputs
dIN4  = Pin(4,  Pin.IN, Pin.PULL_UP)
dIN5  = Pin(5,  Pin.IN, Pin.PULL_UP)
dIN15 = Pin(15, Pin.IN, Pin.PULL_UP)
dIN18 = Pin(18, Pin.IN, Pin.PULL_UP)
dIN19 = Pin(19, Pin.IN, Pin.PULL_UP)
dIN21 = Pin(21, Pin.IN, Pin.PULL_UP)
dIN22 = Pin(22, Pin.IN, Pin.PULL_UP)
dIN23 = Pin(23, Pin.IN, Pin.PULL_UP)
dIN25 = Pin(25, Pin.IN, Pin.PULL_UP)
dIN26 = Pin(26, Pin.IN, Pin.PULL_UP)
dIN27 = Pin(27, Pin.IN, Pin.PULL_UP)
dIN32 = Pin(32, Pin.IN, Pin.PULL_UP)
dIN33 = Pin(33, Pin.IN, Pin.PULL_UP)
dIN34 = Pin(34, Pin.IN, Pin.PULL_UP)    # Valor instável? Pino já utilizado?
dIN35 = Pin(35, Pin.IN, Pin.PULL_UP)    # Valor instável? Pino já utilizado?

# Digital Outputs
dOUT2  = Pin(2,  Pin.OUT, drive=Pin.DRIVE_0) # Embed
dOUT12 = Pin(12, Pin.OUT, drive=Pin.DRIVE_0) # R
dOUT13 = Pin(13, Pin.OUT, drive=Pin.DRIVE_0) # B
dOUT14 = Pin(14, Pin.OUT, drive=Pin.DRIVE_0) # G

utils.startupDiag((dOUT2, dOUT12, dOUT13, dOUT14));

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