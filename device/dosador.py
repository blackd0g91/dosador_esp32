import json
import network
import time
import ntptime
import _arequests
import utils
import machine
import uasyncio
import random
from machine import Pin
from _arequests import Response
from _arequests import TimeoutError
from _arequests import ConnectionError
from _hx711 import HX711

class Dosador:

    SERVER_BASE         = const("https://monitor-pet-dosador.azurewebsites.net/api/")   # URL base da API
    SERVER_APIKEY       = const('e5dd09c6-a4bf-46bf-af56-4c533f5c60aa')                 # Chave da API
    MAX_WEIGHT          = const(500)                                                    # Peso máximo suportado pelo recipiente
    WEIGHT_LIST_SIZE    = const(10)                                                     # Lista de últimos pesos registrados

    def __init__(self, id, utc, releaseBtn, wlanLed, releaseLed, scaleD, scaleSCK):
        self.id             = id                                                        # ID do dosador
        self.utc            = utc                                                       # UTC (-12 a 12)

        self.releaseBtn     = Pin(releaseBtn, Pin.IN, Pin.PULL_UP)                      # Botão para liberação manual da ração

        self.wlanLed        = Pin(wlanLed, Pin.OUT, drive=Pin.DRIVE_0)                  # Led de feedback da WLAN
        self.releaseLed     = Pin(releaseLed, Pin.OUT, drive=Pin.DRIVE_0)               # Led de feedback de motor em funcionamento

        self.schedules      = {}                                                        # Objeto contendo os agendamentos
        self.lastMinChecked = -1                                                        # Flag para identificar qual foi o último minuto em que o agendamento foi verificado
        self.lastWeight     = -1                                                        # Último peso registrado e enviado para o servidor
        self.weightList     = []                                                        # Listagem de últimos pesos registrados para validação


        self.wlan           = self.createWlan()                                         # Objeto da WLAN
        self.rtc            = self.createRTC()                                          # Objeto de Real Time Clock
        self.scale          = self.createScale(scaleD, scaleSCK)                        # Objeto da balança

        # TODO inicializar o tare baseado em valor salvo em arquivo caso exista
        self.tare           = 0                                                         # Offset para valor retornado pela balança (Tara)

    # AGENDAMENTOS

    # Atualiza os agendamentos com o servidor e retorna como objeto dict
    async def getSchedules(self):
        await self.updateSchedules()
        return self.schedules

    # Se possível busca os agendamentos atualizados no servidor e atualiza o objeto interno
    async def updateSchedules(self):

        if self.wlan.isconnected():
            self.releaseLed.on()
            await self.requestUpdatedSchedules()
            self.releaseLed.off()

        if self.schedules == None or self.wlan.isconnected():
            print("Setting schedules")
            schedules = utils.getContent("schedules.json")
            if schedules:
                temp = []
                schedules = json.loads(schedules)
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

        # Imprime os agendamentos (Apenas para testes)
        # if self.schedules:
        #     for schedule in self.schedules:
        #         print(schedule, type(schedule))

    # Verifica se existe algum agendamento para o minuto atual
    async def checkSchedules(self):
        print("Checking schedules")

        dow = self.getCurrentDayOfWeek()
        m   = self.getCurrentMinute()
        h   = self.getCurrentHour()

        if self.schedules:
            for sch in self.schedules:
                if sch["dow"] == dow and sch["h"] == h and sch["m"] == m:
                    return sch

        return {}

    # REQUISIÇÕES

    # Requisição de agendamentos atualizados e armazenamento em arquivo interno
    async def requestUpdatedSchedules(self):
        endpoint = f'ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.SERVER_APIKEY}'
        request = await self.makeRequest("GET", endpoint)
        if isinstance(request, Response):
            utils.storeContent('schedules.json', request.content)
            return request

    async def sendNewWeight(self):
        # TODO criar requisição para envio de peso
        return False

    # Método base para requisições assíncronas
    async def makeRequest(self, method, endpoint, data=None, json=None, headers={}, timeout=10):
        url = self.SERVER_BASE + endpoint
        try:
            return await uasyncio.wait_for(_arequests._requests(method, url, data=data, json=json, headers=headers), timeout=timeout)
        except TimeoutError as e:
            print("TimeoutError", e)
        except ConnectionError as e:
            print("ConnectionError", e)
        except Exception as e:
            print("Exception", e)
        return False
        
            
        

    # TEMPO

    # Cria o objeto RTC (Real Time Clock) do equipamento
    # Caso haja um datetime salvo, assume este horário
    def createRTC(self):
        rtc = machine.RTC()
        datetime = utils.getContent("datetime.json")
        if datetime:
            rtc.init(json.loads(datetime))
        return rtc

    # Sincroniza o relógio interno através de um servidor remoto
    async def updateByNetworkTime(self):
        try:
            ntptime.settime()
            utcTime = time.localtime(time.mktime(time.localtime()) + (self.utc * 3600))
            utcTime = utils.convertTimeToRTC(utcTime)
            self.rtc.init(utcTime)
        except OSError as e:
            self.releaseLed.on()
            if e.errno == errno.ETIMEDOUT:
                await self.updateByNetworkTime()

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
        return self.getDatetime()[4]

    # Retorna o minuto atual
    def getCurrentMinute(self):
        return self.getDatetime()[5]

    # Retorna um inteiro representando o dia da semana atual
    def getCurrentDayOfWeek(self):
        return self.getDatetime()[3]



    # WLAN

    # Cria o objeto de conexão (Wlan)
    def createWlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        return wlan

    # Busca as informações de SSID e senha do arquivo json salvo e tenta realizar a conexão
    async def wlanconnect(self):
        credentials = utils.getwlancredentials()
        try:
            self.wlan.connect(credentials["ssid"], credentials["password"])
        except Exception as e:
            machine.reset()
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
            self.releaseLed.on()
            print("Releasing Food")
            uasyncio.sleep(2)
            self.releaseLed.off()
        else:
            print("Invalid quantity")

    # BALANÇA

    def createScale(self, d, sck):
        return HX711(d_out=d, pd_sck=sck, channel=HX711.CHANNEL_A_64)

    async def getCurrentWeight(self):
        # TODO Buscar da balança real
        return await self.scaleRead()
        # return random.randint(0, 2)

    async def checkWeightChange(self):

        # Atualiza a listagem de pesos com o mais atual
        await self.updateWeightList()

        if len(self.weightList) > 9:
            for weight in self.weightList:
                if self.weightList.count(weight) > self.WEIGHT_LIST_SIZE / 2 and weight != self.lastWeight:
                    self.lastWeight = weight
                    self.weightList = []
                    return weight
        
        return -1        

    async def updateWeightList(self):
        if len(self.weightList) >= self.WEIGHT_LIST_SIZE:
            del self.weightList[0]
        
        currentWeight = await self.getCurrentWeight()
        self.weightList.append(currentWeight)

    ########################################################################################

    def resetScale(self):
        self.scale.power_off()
        self.scale.power_on()

    def setTare(self):
        self.tare = self.scale.read()

    def scaleRawValue(self):
        return self.scale.read() - self.tare

    async def scaleRead(self, reads=10, delay_ms=1):
        values = []
        for _ in range(reads):
            values.append(self.scaleRawValue())
            await uasyncio.sleep_ms(delay_ms)
        return await self._stabilizer(values)

    @staticmethod
    async def _stabilizer(values, deviation=10):
        return round( sum(values) / len(values) )
        # weights = []
        # for prev in values:
        #     weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        # return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]

    ########################################################################################

    # BOTÕES

    async def releaseAction(self):
        print("Pressed")
        self.releaseLed.on()




        # set schedules attribute
        # await self.updateSchedules()
        




        while self.releaseBtn.value() == 0:
            await uasyncio.sleep_ms(100)
        self.releaseLed.off()