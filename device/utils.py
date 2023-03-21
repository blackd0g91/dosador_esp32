import esp32
import json
import os

try:
    os.listdir('storage')
    print('Storage folder already exists')
except OSError:
    print('Creating storage folder')
    os.mkdir('storage')

def storeContent(filename, content):
    f = open('storage/'+filename, 'w')
    f.write(content)
    f.close()

def getContent(filename):
    f = open('storage/'+filename, 'r')
    content = f.read()
    f.close()
    return content

def getTemperature(self):
    celsius = (esp32.raw_temperature() - 32) * (5/9)
    return celsius

# Resgata dados da WLAN do arquivo
def getwlancredentials():
    wlanFile = open("wlan.json", "r")
    wlanInfo = json.loads(wlanFile.read())
    return wlanInfo