import pathlib

import requests
import json

from weather_utils import GetData_DB
from geolocation import Openweather_Geolocation, Accuweather_Geolocation, Matcher

# /////////////////////////////////////   ACCUWEATHER-CURRENT    ///////////////////////////////////////////////////// #
class Current_Accuweather(Matcher, GetData_DB):

    def __init__(self):
        # Obtener APIKEY de Openweather
        self.apikey = self.get_apikey('Accuweather')

        # Variables climatológicas de Accuweather
        self.local_time = None
        self.epoch_time = None
        self.weather_text = None
        self.weather_icon = None
        self.has_precipitation = None
        self.precipitation_type = None
        self.is_daytime = None
        self.temp_metric = None
        self.unit_metric = None
        self.filtered_descrip = None

        # Agregar logging

    def get_current_data(self):
        """Se obtiene los datos climaticos actuales por Accuweather."""

        # Realiza la verificación de la ciudad
        #self.verify_city_match(service='Accuweather')

        #
        if self.verify_city_match(service='Accuweather') is True:

            # Obtiene los datos del clima actual de la ciudad por medio de la api del servicio:
            try:
                url = f"http://dataservice.accuweather.com/currentconditions/v1/{self.city_key}"
                parameters = {
                    'apikey': self.apikey,
                    'language': 'es'
                }

                reply = requests.get(url, params=parameters)

                if reply.status_code == 200:
                    data = reply.json()

                    print("Accuweather: Se obtuvieron los datos correctamente.")
                    return data

                elif reply.status_code == 400:
                    print("400 - Error: Error de sintaxis.")

                elif reply.status_code == 401:
                    print("401 - Unauthorized: clave inválida.")

                elif reply.status_code == 403:
                    print("403 - Unauthorized: no tiene permiso para solicitar este recurso.")

                elif reply.status_code == 404:
                    print("Too Many Requests: Límite de llamadas superado.")

                else:
                    print("Accuweather: Error al obtener los datos del servidor.")

            except requests.exceptions as e:
                print("Error: ", e)

    def accu_extract_data(self):  # 2
        """Extrae la información del pronostico de la solicitud recibida en cada variable establecida."""

        data = self.get_current_data()

        if data:
            # Extraer datos individuales
            self.local_time = data[0]['LocalObservationDateTime']
            self.epoch_time = data[0]['EpochTime']
            self.weather_text = data[0]['WeatherText']
            self.weather_icon = data[0]['WeatherIcon']
            self.has_precipitation = data[0]['HasPrecipitation']
            self.precipitation_type = data[0]['PrecipitationType']
            self.is_daytime = data[0]['IsDayTime']

            # Extraer temperatura en unidades métricas e imperiales
            self.temp_metric = round(data[0]['Temperature']['Metric']['Value'])
            self.unit_metric = data[0]['Temperature']['Metric']['Unit']
            # Diccionario español y adaptado a frases cotidianas
            self.filtered_descrip = self.dictionary_description(service='Accuweather', condition=self.weather_icon)

            return True

        return  False

# /////////////////////////////////////   OPENWEATHER-CURRENT    ///////////////////////////////////////////////////// #
class Current_Openweather(Matcher, GetData_DB):

    def __init__(self):
        # Obtener APIKEY de Openweather
        self.apikey = self.get_apikey('Openweather')

        # Variables climáticas de Openweather
        self.weather = None
        self.description = None
        self.temp = None
        self.feels_like = None
        self.temp_min = None
        self.temp_max = None
        self.pressure = None
        self.humidity = None
        self.visibility = None
        self.wind_speed = None
        self.wind_deg = None
        self.wind_gust = None
        self.sunrise = None
        self.sunset = None
        self.conversion_visibility = None

        # Obtener la información del diccionario de JSON
        path = pathlib.Path(
            r'C:\Users\Be-Nicko\Documents\PycharmProjects\Asistente2G\services\weather_service\descriptions.json')

        with open(path, 'r', encoding='utf-8') as file:
            self.dict_descriptions = json.load(file)

    def get_current_data(self):  # 1
        """Se obtiene los datos climaticos actuales por Openweather."""

        # Realiza la verificación de la ciudad
        self.verify_city_match(service='Openweather')

        if self.verify_city_match(service='Openweather') is True:

            # Obtiene los datos del clima actual de la ciudad por medio de la api del servicio:
            try:
                url = (f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}"
                        f"&appid={self.apikey}&units=metric")

                reply = requests.get(url)

                if reply.status_code == 200:
                    data = reply.json()

                    print("Openweather: Se obtuvieron los datos correctamente.")
                    return data

                elif reply.status_code == 401:
                    print("401 - Unauthorized: clave inválida.")

                elif reply.status_code == 404:
                    print("404 - Not Found: no existe el recurso solicitado.")

                elif reply.status_code == 429:
                    print("Too Many Requests: Límite de llamadas superado.")

                else:
                    print("Openweather: Error al obtener los datos del servidor.")

            except Exception as e:
                print("Error: ", e)

        else:
            print("Error en la validación.")

    def open_extract_data(self):  # 2
        """Extrae la información del pronostico de la solicitud recibida en cada variable establecida."""

        data = self.get_current_data()

        if data:

            # Información principal:
            self.weather = data['weather'][0]['main']  # String
            self.description = data['weather'][0]['description']  # String

            # Temperaturas:
            self.temp = round(data['main']['temp'])  # Centigrados
            self.feels_like = round(data['main']['feels_like'])  # Centigrados
            self.temp_min = round(data['main']['temp_min'])  # Centigrados
            self.temp_max = round(data['main']['temp_max'])  # Centigrados

            # Varios:
            self.pressure = data['main']['pressure']  # HectoPascales /hPa.
            self.humidity = data['main']['humidity']  # Porcentaje
            self.visibility = data['visibility']  # Kilómetros /Km.

            # Viento:
            self.wind_speed = data['wind']['speed']  # Velocidad del viento en m/s
            self.wind_deg = data['wind']['deg']  # Dirección del viento en grados
            self.wind_gust = data['wind']['gust']  # Ráfagas m/s

            self.sunrise = data['sys']['sunrise']  # Salida del sol - Horarios en timestamp
            self.sunset = data['sys']['sunset']  # Puesta del sol - Horarios en timestamp

            # Diccionario español y adaptado a frases cotidianas
            self.filtered_descrip = self.dictionary_description(service='Openweather', condition=self.description)
            self.conversion_visibility = self.conversion_metrics(self.visibility)  # Calclua distancia de visibilidad
            self.conversion_wind_deg = self.wind_convert(self.wind_deg)  # Calcula dirección del viento
            self.conversion_time(self.sunrise, self.sunset)  # Revisar

            return True

        else:
            print("Openweather: Error al extraer datos climáticos de la solicitud.")

        return False

