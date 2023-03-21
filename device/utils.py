import esp32
import json

def getTemperature(self):
    celsius = (esp32.raw_temperature() - 32) * (5/9)
    return celsius

# Resgata dados da WLAN do arquivo
def getwlancredentials():
    wlanFile = open("wlan.json", "r")
    wlanInfo = json.loads(wlanFile.read())
    return wlanInfo