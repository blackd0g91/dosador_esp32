import esp32
import urequests

class Dosador:

    def __init__(self, id, apiKey):
        self.id     = id
        self.apiKey = apiKey

    def getTemperature(self):
        celsius = (esp32.raw_temperature() - 32) * (5/9)
        return celsius

    # TODO: Criar função genérica para requisições com o objetivo de armazenar possíveis constantes
    def getSchedules(self):
        url = f'https://monitor-pet-dosador.azurewebsites.net/api/ScheduleFunction?IdDosador={self.id}&KeyAccessApi={self.apiKey}'
        print(url)
        response = urequests.get(url)
        print(response.content)