import json
import network
import time
import urequests
import utils

SERVER_BASE = "https://monitor-pet-dosador.azurewebsites.net/api/"

class Dosador:

    def __init__(self, id, apiKey):
        self.id     = id
        self.apiKey = apiKey

    def updateSchedules(self):
        endpoint = f'ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.apiKey}'
        request = self.makeRequest("GET", endpoint)
        utils.storeContent('schedules.json', request.content)
        return request

    def getSchedules(self):
        return utils.getContent('schedules.json')

    def makeRequest(self, method, endpoint, data=None, json=None, headers={}):
        url = SERVER_BASE + endpoint
        response = urequests.request(method, url, data=None, json=None, headers={})
        return response

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