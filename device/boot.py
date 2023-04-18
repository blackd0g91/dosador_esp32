print("=================================================")
print("=================================================")
print("=================================================")
# This file is executed on every boot (including wake-boot from deepsleep)
import time
import network
import json
import machine
from machine import Pin
import dosador
from dosador import Dosador
import utils
import uasyncio
import esp
import micropython

# Digital Inputs
# dIN4  = Pin(4,  Pin.IN, Pin.PULL_UP)
# dIN5  = Pin(5,  Pin.IN, Pin.PULL_UP)
# dIN15 = Pin(15, Pin.IN, Pin.PULL_UP)
# dIN18 = Pin(18, Pin.IN, Pin.PULL_UP)
# dIN19 = Pin(19, Pin.IN, Pin.PULL_UP)
# dIN21 = Pin(21, Pin.IN, Pin.PULL_UP)
# dIN22 = Pin(22, Pin.IN, Pin.PULL_UP)
# dIN23 = Pin(23, Pin.IN, Pin.PULL_UP)
# dIN25 = Pin(25, Pin.IN, Pin.PULL_UP)
# dIN26 = Pin(26, Pin.IN, Pin.PULL_UP)
# dIN27 = Pin(27, Pin.IN, Pin.PULL_UP)
# dIN32 = Pin(32, Pin.IN, Pin.PULL_UP)
# dIN33 = Pin(33, Pin.IN, Pin.PULL_UP)
# dIN34 = Pin(34, Pin.IN, Pin.PULL_UP)    # Valor instável? Pino já utilizado?
# dIN35 = Pin(35, Pin.IN, Pin.PULL_UP)    # Valor instável? Pino já utilizado?

# Digital Outputs
dOUT2  = Pin(2,  Pin.OUT, drive=Pin.DRIVE_0) # Embed
# dOUT12 = Pin(12, Pin.OUT, drive=Pin.DRIVE_0) # R
# dOUT13 = Pin(13, Pin.OUT, drive=Pin.DRIVE_0) # B
# dOUT14 = Pin(14, Pin.OUT, drive=Pin.DRIVE_0) # G

# utils.startupDiag(
#     (2, 12, 13, 14)
# )