import json
import network
import time
import ntptime
import urequests
import utils
import machine
import uasyncio

class Dosador:

    SERVER_BASE = "https://monitor-pet-dosador.azurewebsites.net/api/"
    SERVER_APIKEY = 'e5dd09c6-a4bf-46bf-af56-4c533f5c60aa'

    def __init__(self, id, utc, wlanLed, releaseBtn, releaseLed):
        self.id     = id
        self.utc = utc
        self.wlanLed = wlanLed
        self.releaseBtn = releaseBtn
        self.releaseLed = releaseLed
        self.flag = -1
        self.wlan = self.createWlan()

    # AGENDAMENTOS

    def updateSchedules(self):
        # endpoint = f'ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.apiKey}'
        endpoint = f'ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.SERVER_APIKEY}'
        request = self.makeRequest("GET", endpoint)
        utils.storeContent('schedules.json', request.content)
        return request

    def getSchedules(self):
        return utils.getContent('schedules.json')

    # REQUISIÇÕES

    def makeRequest(self, method, endpoint, data=None, json=None, headers={}):
        url = self.SERVER_BASE + endpoint
        response = urequests.request(method, url, data=None, json=None, headers={})
        return response

    # TEMPO

    async def updateByNetworkTime(self):
        ntptime.settime()

    def getTimeUTC(self):
        utcTime = time.mktime(time.localtime()) + ( self.utc * 3600)
        return time.localtime(utcTime)

    def getReadableTime(self):
        t = self.getTimeUTC()
        return f'{utils.twoDigit(t[2])}/{utils.twoDigit(t[1])}/{t[0]}, {utils.DIAS_SEMANA[t[6]]} - {utils.twoDigit(t[3])}:{utils.twoDigit(t[4])}:{utils.twoDigit(t[5])}'

    def getUSDate(self):
        t = self.getTimeUTC()
        return f'{t[0]}-{utils.twoDigit(t[1])}-{utils.twoDigit(t[2])}'

    # WLAN

    def createWlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        return wlan

    async def wlanconnect(self):
        credentials = utils.getwlancredentials()
        self.wlan.connect(credentials["ssid"], credentials['password'])
        await self.wlanAttemptingToConnect()
        await self.updateByNetworkTime()

    async def wlanAttemptingToConnect(self):
        while not self.wlan.isconnected():
            print("Connecting...")
            self.wlanLed.value(not self.wlanLed.value())
            await uasyncio.sleep_ms(500)
        self.wlanLed.off()
        print("Connected")

    # BOTÕES

    async def releaseAction(self):
        print("Pressed")

        while self.releaseBtn.value() == 0:
            self.releaseLed.on()
            await uasyncio.sleep_ms(100)
        self.releaseLed.off()

    # INTERRUPÇÕES

    def releasePressed(self, Pin):
        if self.flag == -1 or time.localtime()[4] != self.flag:
            self.flag = time.localtime()[4]
            print("Pressed")
            if self.releaseBtn.value() == 1:
                self.releaseLed.on()
            else:
                self.releaseLed.off()