# This file is executed on every boot (including wake-boot from deepsleep)
import time
import network
from machine import Pin
from dosador import Dosador

# Digital Inputs
dIN2  = Pin(2,  Pin.IN, Pin.PULL_UP)
dIN4  = Pin(4,  Pin.IN, Pin.PULL_UP)
dIN5  = Pin(5,  Pin.IN, Pin.PULL_UP)
dIN12 = Pin(12, Pin.IN, Pin.PULL_UP)
dIN14 = Pin(14, Pin.IN, Pin.PULL_UP)
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
dOUT13 = Pin(13, Pin.OUT)

# Interrupts
# dIN33.irq(Pin.IRQ_FALLING, callback)