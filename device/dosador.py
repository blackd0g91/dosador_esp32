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
from _arequests import Response, TimeoutError, ConnectionError
from _hx711 import HX711

class Dosador:

    SERVER_BASE         = const("https://monitor-pet-dosador.azurewebsites.net/api/")   # URL base da API
    SERVER_APIKEY       = const('e5dd09c6-a4bf-46bf-af56-4c533f5c60aa')                 # Chave da API
    MAX_WEIGHT          = const(500)                                                    # Peso máximo suportado pelo recipiente
    WEIGHT_LIST_SIZE    = const(10)                                                     # Lista de últimos pesos registrados
    SCALE_CALIBRATOR    = const(1120)                                                   # Valor para calibração da balança (8960/8)

    def __init__(self, id, utc, tareBtn, releaseBtn, wlanLed, tareLed, releaseLed, scaleD, scaleSCK):
        self.id             = id                                                        # ID do dosador
        self.utc            = utc                                                       # UTC (-12 a 12)

        self.tareBtn        = Pin(tareBtn, Pin.IN, Pin.PULL_UP)                         # Botão para atualizar a tara da balança
        self.releaseBtn     = Pin(releaseBtn, Pin.IN, Pin.PULL_UP)                      # Botão para liberação manual da ração

        self.wlanLed        = Pin(wlanLed, Pin.OUT, drive=Pin.DRIVE_0)                  # Led de feedback da WLAN
        self.tareLed        = Pin(tareLed, Pin.OUT, drive=Pin.DRIVE_0)                  # Led de feedback do botão de tara
        self.releaseLed     = Pin(releaseLed, Pin.OUT, drive=Pin.DRIVE_0)               # Led de feedback de motor em funcionamento

        self.schedules      = {}                                                        # Objeto contendo os agendamentos
        self.lastMinChecked = -1                                                        # Flag para identificar qual foi o último minuto em que o agendamento foi verificado
        self.lastWeight     = self.getMemoryWeight()                                    # Último peso registrado e enviado para o servidor
        self.weightList     = []                                                        # Listagem de últimos pesos registrados para validação
        self.tare           = self.getMemoryTare()                                      # Offset para valor retornado pela balança (Tara)

        self.wlan           = self.createWlan()                                         # Objeto da WLAN
        self.rtc            = self.createRTC()                                          # Objeto de Real Time Clock
        self.scale          = self.createScale(scaleD, scaleSCK)                        # Objeto da balança

        self.wlanLed.on()
        self.tareLed.on()
        self.releaseLed.on()
        
        print("Tare Button: ", self.tareBtn, " - Tare LED: ", self.tareLed)
        print("Release Button:", self.releaseBtn, " - Release LED: ", self.releaseLed)
        print("WLAN LED: ", self.wlanLed)
        print("Scale D: ", scaleD, "Scale SCK", scaleSCK)
        print("Last Weight: ", self.lastWeight)
        print("Tare: ", self.tare)

        self.wlanLed.off()
        self.tareLed.off()
        self.releaseLed.off()

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

                # TODO Incluir aqui a verificação para liberação imediata
                if schedules['lastRelease'] != None:
                    print(schedules['lastRelease'], type(schedules['lastRelease']))
                    # Avaliar horário, caso seja mais antigo que 5 minutos, desconsiderar
                else:
                    print("lastRelease not set")

                for schedule in schedules['schedules']:

                    time = schedule['scheduledDate'].split(":")
                    dow = utils.DIAS_SEMANA_SERVER[ schedule['dayOfWeek'] ]

                    tempSchedule = {
                        'id'    : schedule['idSchedule'],   # ID do Agendamento
                        'qtt'   : schedule['quantity'],     # Quantidade de alimento a ser liberado (em gramas)
                        'dow'   : dow,                      # Dia da semana do agendamento
                        'h'     : time[0],                  # Hora do agendamento
                        'm'     : time[1]                   # Minuto do agendamento
                    }
                    temp.append(tempSchedule)

                self.schedules = temp

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

    async def sendNewWeight(self, weight):
        endpoint = f'AddWeightFunction?KeyAccessApi={self.SERVER_APIKEY}'
        parameters = {
            'idDosador': self.id,
            'weight'   : weight
        }
        request = await self.makeRequest("POST", endpoint, json=parameters)
        if(request.status_code == 201):
            return True
        else:
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

    async def releaseFood(self, quantity=0):
        if quantity > 0 and quantity <= self.MAX_WEIGHT:

            self.releaseLed.on()

            reading = -1        # Leitura da balança
            retryCount = 0      # Contador para retentativas caso o valor da balança não se altere(estoque vazio)
            maxRetries = 25     # Máximo de tentativas para aguardar até que o peso seja alterado(estoque vazio)

            while True:
                newReading = await self.scaleRead()

                if(newReading == reading):
                    retryCount = retryCount + 1
                else:
                    retryCount = 0

                reading = newReading

                if reading >= quantity or retryCount >= maxRetries:
                    break

                await uasyncio.sleep_ms(200)
                

            self.releaseLed.off()

        else:
            print("Invalid quantity")

    #
    # BALANÇA
    #

    def createScale(self, d, sck):
        return HX711(d_out=d, pd_sck=sck, channel=HX711.CHANNEL_A_64)

    async def checkWeightChange(self):

        # Atualiza a listagem de pesos com o mais atual
        await self.updateWeightList()

        if len(self.weightList) > 9:
            for weight in self.weightList:
                if self.weightList.count(weight) > self.WEIGHT_LIST_SIZE / 2 and weight != self.lastWeight:
                    if self.sendNewWeight(weight):
                        self.lastWeight = weight
                        weight = str(weight)
                        utils.storeContent('lastWeight.txt', weight)
                        self.weightList = []
                        return self.lastWeight
                    else:
                        return False
        
        return -1        

    async def updateWeightList(self):
        if len(self.weightList) >= self.WEIGHT_LIST_SIZE:
            del self.weightList[0]
        
        currentWeight = await self.scaleRead()
        self.weightList.append(currentWeight)

    def getMemoryTare(self):
        print("Getting memory tare")
        tare = utils.getContent("tare.txt");
        if not tare or tare == '':
            return False
        else:
            return float(tare)

    def getMemoryWeight(self):
        print("Getting memory weight")
        weight = utils.getContent("lastWeight.txt")
        if not weight or weight == '':
            return -1
        else:
            return int(weight)

    async def setTare(self, count=100, delay_ms=1):
        self.tareLed.on()
        tares = []
        for _ in range(0, count):
            tares.append(self.scale.read())
            await uasyncio.sleep_ms(delay_ms)
        tare = sum(tares)/len(tares)
        self.tare = tare
        utils.storeContent("tare.txt", str(tare))
        print(f'New tare set to {tare}')
        self.weightList = []
        self.tareLed.off()
        return tare

    # Retorna o valor atual de uma leitura da balança, removendo a tara e aplicando a calibração
    def scaleRawValue(self):
        return ( ( self.scale.read() - self.tare ) / self.SCALE_CALIBRATOR )

    # Retorna o valor médio de múltiplas leituras
    async def scaleRead(self, reads=10, delay_ms=1):
        values = []
        for _ in range(reads):
            values.append(self.scaleRawValue())
            await uasyncio.sleep_ms(delay_ms)
        return await self._stabilizer(values)

    @staticmethod
    async def _stabilizer(values, deviation=10):
        # print(sum(values)/len(values))
        return round( sum(values) / len(values) )
        # weights = []
        # for prev in values:
        #     weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        # return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]

    #
    # BOTÕES
    #

    # Ação do botão de tara
    async def tareAction(self):
        await self.setTare()
        for _ in range(0, 25):
            self.tareLed.value(not self.tareLed.value())
            await uasyncio.sleep_ms(200)
        self.tareLed.off()

    # Ação do botão de liberação manual
    async def releaseAction(self):
        print("Pressed")
        self.releaseLed.on()




        # set schedules attribute
        # await self.updateSchedules()
        # await self.sendNewWeight()
        




        while self.releaseBtn.value() == 0:
            await uasyncio.sleep_ms(100)
        self.releaseLed.off()