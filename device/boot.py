print("=================================================")
print("=================================================")
print("=================================================")

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

dOUT2  = Pin(2,  Pin.OUT, drive=Pin.DRIVE_0) # Embed