import esp32
import time
import json
import os
import machine

try:
    os.listdir('storage')
except OSError:
    print('Creating storage folder')
    os.mkdir('storage')

DIAS_SEMANA = ('SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM')
DIAS_SEMANA_SERVER = (6, 0, 1, 2, 3, 4, 5)

# Armazena uma string em arquivo, caso já exista, sobrescreve o conteúdo
def storeContent(filename, content):
    f = open('storage/'+filename, 'w')
    f.write(content)
    f.close()

# Busca o conteúdo de um arquivo
def getContent(filename):
    try:
        f = open('storage/'+filename, 'r')
        content = f.read()
        f.close()
        return content
    except OSError as e:
        if hasattr(e, 'errno'):
            if e.errno == errno.ENOENT:
                print(f'ERROR: File {filename} does not exist.')
                print(f'File {filename} does not exist, creating it...')
                storeContent(filename, '')
        return False

# Busca a temperatura atual do microcontrolador
def getTemperature():
    celsius = (esp32.raw_temperature() - 32) * (5/9)
    return round(celsius, 1)

# Resgata dados da WLAN do arquivo
def getwlancredentials():
    wlanFile = getContent("wlan.json")
    wlanInfo = json.loads(wlanFile)
    return wlanInfo

# Converte do formato do módulo time para o formato da classe RTC
def convertTimeToRTC(datetime):
    return (
        datetime[0],
        datetime[1],
        datetime[2],
        datetime[6],
        datetime[3],
        datetime[4],
        datetime[5],
        datetime[6]
    )

# Normaliza números abaixo de 10 para duas casas
# Ex: 1 -> 01
def twoDigit(number):
    if number < 10:
        return '0' + str(number)
    else:
        return str(number)

# Método para imprimir valores do microcontrolador
def startupDiag():
    print("CPU Frequency:", machine.freq() / 1000000, "MHz")
