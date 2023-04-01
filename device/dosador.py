import json
import network
import time
import ntptime
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

        self.schedules      = {}
        self.lastMinChecked = -1

        self.wlan           = self.createWlan()
        self.rtc            = self.createRTC()

    # AGENDAMENTOS

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

                temp = []

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
                    temp.append(tempSchedule)

                self.schedules = temp
        else:
            print("Schedules already set")

        # Imprime os agendamentos (Apenas para testes)
        if self.schedules:
            for schedule in self.schedules:
                print(schedule, type(schedule))

    async def checkSchedules(self):
        print("Checking schedules")

        dow = self.getCurrentDayOfWeek()
        m   = self.getCurrentMinute()
        h   = self.getCurrentHour()

        if self.schedules:
            for sch in self.schedules:
                if sch.dow == dow and sch.h == h and sch.m == m:
                    return sch

        return {}

    # REQUISIÇÕES

    async def requestUpdatedSchedules(self):
        endpoint = f'ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.SERVER_APIKEY}'
        request = await self.makeRequest("GET", endpoint)
        if isinstance(request, Response):
            utils.storeContent('schedules.json', request.content)
            return request

    async def makeRequest(self, method, endpoint, data=None, json=None, headers={}, timeout=10):
        url = self.SERVER_BASE + endpoint
        try:
            return await uasyncio.wait_for(arequests._requests(method, url, data=data, json=json, headers=headers), timeout=timeout)
        except uasyncio.TimeoutError as e:
            # raise TimeoutError(e)
            print("TimeoutError", e)
            return False
        
            
        

    # TEMPO

    # Cria o objeto RTC (Real Time Clock) do equipamento
    # Caso haja um datetime salvo, assume o horário fornecido por ele
    def createRTC(self):
        rtc = machine.RTC()
        datetime = utils.getContent("datetime.json")
        if datetime:
            rtc.init(json.loads(datetime))
        return rtc

    # Sincroniza o relógio interno através de um servidor remoto
    async def updateByNetworkTime(self):
        ntptime.settime()
        utcTime = time.localtime(time.mktime(time.localtime()) + (self.utc * 3600))
        utcTime = utils.convertTimeToRTC(utcTime)
        self.rtc.init(utcTime)

    # Retorna uma tupla com os dados de data e horário
    def getDatetime(self):
        return self.rtc.datetime()

    # Retorna uma string com data e horário atuais formatados para leitura
    def getReadableTime(self):
        t = self.getDatetime()
        return f'{utils.twoDigit(t[2])}/{utils.twoDigit(t[1])}/{t[0]}, {utils.DIAS_SEMANA[t[3]]} - {utils.twoDigit(t[4])}:{utils.twoDigit(t[5])}:{utils.twoDigit(t[6])}'

    # Retorna uma string no formato YYYY-MM-DD
    def getCurrentUSDate(self):
        t = self.getDatetime()
        return f'{t[0]}-{utils.twoDigit(t[1])}-{utils.twoDigit(t[2])}'

    # Retorna a hora atual
    def getCurrentHour(self):
        return self.getDatetime()[3]

    # Retorna o minuto atual
    def getCurrentMinute(self):
        return self.getDatetime()[4]

    # Retorna um inteiro representando o dia da semana atual
    def getCurrentDayOfWeek(self):
        return self.getDatetime()[6]



    # WLAN

    # Cria o objeto de conexão (Wlan)
    def createWlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        return wlan

    # Busca as informações de SSID e senha do arquivo json salvo e tenta realizar a conexão
    async def wlanconnect(self):
        credentials = utils.getwlancredentials()
        print("SSID", credentials["ssid"])
        print("password", credentials["password"])
        self.wlan.connect(credentials["ssid"], credentials["password"])
        await self.wlanAttemptingToConnect()
        await self.updateByNetworkTime()

    # Informa através de um LED e pelo console uma tentativa de conexão
    async def wlanAttemptingToConnect(self):
        while not self.wlan.isconnected():
            print("Connecting...")
            for x in range(4):
                self.wlanLed.value(not self.wlanLed.value())
                await uasyncio.sleep_ms(250)
        self.wlanLed.on()
        print("Connected")

    # MOTOR

    def releaseFood(self, quantity=0):
        if quantity > 0:
            print("Releasing Food")
        else:
            print("Invalid quantity")

    # BOTÕES

    async def releaseAction(self):
        print("Pressed")
        self.releaseLed.on()




        # set schedules attribute
        # await self.updateSchedules()
        utils.storeContent("datetime.json", json.dumps(self.getDatetime()))




        while self.releaseBtn.value() == 0:
            await uasyncio.sleep_ms(100)
        self.releaseLed.off()