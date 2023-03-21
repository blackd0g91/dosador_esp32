import json
import network
import time
import urequests
import utils

class Dosador:

    def __init__(self, id, apiKey):
        self.id     = id
        self.apiKey = apiKey

    # TODO: Criar função genérica para requisições com o objetivo de armazenar possíveis constantes
    def getSchedules(self):
        url = f'https://monitor-pet-dosador.azurewebsites.net/api/ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.apiKey}'
        print(url)
        response = urequests.get(url)
        print(response.content)

    def wlanconnect(self, feedbackPin):
        credentials = utils.getwlancredentials()

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(credentials["ssid"], credentials['password'])
        while not wlan.isconnected():
            print("Connecting...")
            time.sleep(0.2)
            feedbackPin.on()
            time.sleep(0.2)
            feedbackPin.off()
        print("Connected")
        self.wlan = wlan
        return wlan