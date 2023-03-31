import esp32
import time
import json
import os

try:
    os.listdir('storage')
    print('Storage folder already exists')
except OSError:
    print('Creating storage folder')
    os.mkdir('storage')

DIAS_SEMANA = (
    'Segunda-Feira',
    'Terça-Feira',
    'Quarta-Feira',
    'Quinta-Feira',
    'Sexta-Feira',
    'Sábado',
    'Domingo'
    )

DIAS_SEMANA_SERVER = (6, 0, 1, 2, 3, 4, 5)

def storeContent(filename, content):
    f = open('storage/'+filename, 'w')
    f.write(content)
    f.close()

def getContent(filename):
    try:
        f = open('storage/'+filename, 'r')
        content = f.read()
        f.close()
        return content
    except OSError as e:
        if hasattr(e, 'errno'):
            if e.errno == errno.ENOENT:
                print(f'File {filename} does not exist, creating it...')
                storeContent(filename, '')
        return False

def getTemperature():
    celsius = (esp32.raw_temperature() - 32) * (5/9)
    return round(celsius, 1)

# Resgata dados da WLAN do arquivo
def getwlancredentials():
    wlanFile = open("wlan.json", "r")
    wlanInfo = json.loads(wlanFile.read())
    wlanFile.close()
    return wlanInfo

def twoDigit(number):
    if number < 10:
        return '0' + str(number)
    else:
        return str(number)

# Função auxiliar para verificar conexão física de leds
def startupDiag(leds=None):
    if leds != None:
        for led in leds:
            led.on()
            time.sleep_ms(100)
        time.sleep(1)
        for led in leds:
            led.off()