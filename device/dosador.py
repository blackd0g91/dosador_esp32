import json
import network
import time
import ntptime
import urequests
import arequests
import utils
import machine
import uasyncio

class Dosador:

    SERVER_BASE = "https://monitor-pet-dosador.azurewebsites.net/api/"
    SERVER_APIKEY = 'e5dd09c6-a4bf-46bf-af56-4c533f5c60aa'

    def __init__(self, id, utc, wlanLed, releaseBtn, releaseLed):
        self.id             = id
        self.utc            = utc
        self.wlanLed        = wlanLed
        self.releaseBtn     = releaseBtn
        self.releaseLed     = releaseLed

        self.schedules      = None
        self.lastMinChecked = None

        self.wlan           = self.createWlan()
        self.rtc            = self.createRTC()

    # AGENDAMENTOS

    async def requestUpdatedSchedules(self):
        endpoint = f'ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.SERVER_APIKEY}'
        request = await self.makeRequest("GET", endpoint)
        if isinstance(request, Response):
            utils.storeContent('schedules.json', request.content)
            return request

    async def getSchedules(self):
        await self.updateSchedules()
        return self.schedules

    async def updateSchedules(self):

        if self.schedules == None:
            print("Setting schedules")
            await self.requestUpdatedSchedules()
            schedules = utils.getContent("schedules.json")
            if schedules != False:
                schedules = json.loads(schedules)

                tempSchedules = []

                for schedule in schedules:

                    datetime = schedule['scheduledDate'].split("T")[1]
                    datetime = datetime.split(":")

                    dow = utils.DIAS_SEMANA_SERVER[schedule['dayOfWeek']]

                    tempSchedule = {
                        'id'    : schedule['idSchedule'],   # ID do Agendamento
                        'qtt'   : schedule['quantity'],     # Quantidade de alimento a ser liberado (em gramas)
                        'dow'   : dow,                      # Dia da semana do agendamento
                        'h'     : datetime[0],              # Hora do agendamento
                        'm'     : datetime[1]               # Minuto do agendamento
                    }
                    tempSchedules.append(tempSchedule)

                self.schedules = tempSchedules
        else:
            print("Schedules already set")

        # Imprime os agendamentos (Apenas para testes)
        if type(self.schedules) == list and self.schedules:
            for schedule in self.schedules:
                print(schedule, type(schedule))

    # REQUISIÇÕES

    async def makeRequest(self, method, endpoint, data=None, json=None, headers={}, timeout=10):
        url = self.SERVER_BASE + endpoint
        try:
            return await uasyncio.wait_for(arequests._requests(method, url, data=None, json=None, headers={}), timeout=timeout)
        except uasyncio.TimeoutError as e:
            # raise TimeoutError(e)
            print("TimeoutError", e)
            return False
        
            
        

    # TEMPO

    def createRTC(self):
        # Verificar se existe um horário salvo para ser atribuído
        return machine.RTC()

    async def updateByNetworkTime(self):
        ntptime.settime()
        utcTime = time.mktime(time.localtime()) + ( self.utc * 3600)
        self.rtc = time.localtime(utcTime)

    def getTimeUTC(self):
        return self.rtc.datetime()

    def getReadableTime(self):
        t = self.rtc.datetime()
        return f'{utils.twoDigit(t[2])}/{utils.twoDigit(t[1])}/{t[0]}, {utils.DIAS_SEMANA[t[6]]} - {utils.twoDigit(t[3])}:{utils.twoDigit(t[4])}:{utils.twoDigit(t[5])}'

    def getUSDate(self):
        t = self.rtc.datetime()
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
            for x in range(4):
                self.wlanLed.value(not self.wlanLed.value())
                await uasyncio.sleep_ms(250)
        self.wlanLed.on()
        print("Connected")

    # BOTÕES

    async def releaseAction(self):
        print("Pressed")
        self.releaseLed.on()




        # set schedules attribute
        await self.updateSchedules()




        while self.releaseBtn.value() == 0:
            await uasyncio.sleep_ms(100)
        self.releaseLed.off()