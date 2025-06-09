import random

from current_weather import Current_Accuweather, Current_Openweather

class Current_Data():

    def __init__(self):
        self.current_accu = Current_Accuweather()
        self.current_open = Current_Openweather()

    def orchestrate_weather_data(self, service):
        """Se encarga de obtener los datos del clima, gestionando automaticamente el fallo del funcionamiento
         de alguna API del servicio climático y resolviendo el error."""

        # Verificar si los datos de AccuWeather son válidos
        if service == 'accuweather':

            if self.current_accu.accu_extract_data() is not False:
                return 'accuweather'

        if service == 'openweather':
            current_open = self.current_open.open_extract_data()
            return 'openweather'

                #mensaje = "Error en obtener información de las API."
                #Agreagar mensage tts

    def weather_data_get(self, service, request):  # por ejemplo en la BD se guarda el metodo mas el tipo de funcion que encesita, descripcion, temperatura, etc

        orchestrate_weather = self.orchestrate_weather_data(service)

        # Para manejar eventos de Accuweather
        if orchestrate_weather == 'accuweather':
            if request == 'description':
                # Descripción
                reply = [f"El clima actualmente se encuentra {self.current_accu.filtered_descrip}.",
                         f"En este momento, el clima está {self.current_accu.filtered_descrip}.",
                         f"Las condiciones climáticas reflejan un entorno {self.current_accu.filtered_descrip}.",
                         f"Acrualmente se observa un clima {self.current_accu.filtered_descrip}."]

                return random.choice(reply)

            elif request == 'temperature':
                # Temperatura
                reply = [f"La temperatura actual es de {self.current_accu.temp_metric} grados.",
                         f"En este momento, la temperatura es de {self.current_accu.temp_metric} grados.",
                         f"Se registra una temperatura de {self.current_accu.temp_metric} grados en este momento.",
                         f"Según el reporte, estamos a {self.current_accu.temp_metric} grados."]

                print(random.choice(reply))
                return random.choice(reply)

            elif request == 'precipitation':
                # Probabilidad de pricipitación: boolean
                precipitation = self.current_accu.has_precipitation    # SUMAR TIPO DE PRECIPITACION = Precipitation Type

                if precipitation is False:
                    # Sin lluvias
                    reply = ["En este momento, no hay ninguna señal de precipitaciones.",
                             "Las condiciones actuales no muestran lluvia prevista.",
                             "La probabilidad de lluvia es nula en este momento",
                             "La previsión muestra que hoy no habrá lluvias."]

                    return random.choice(reply)

                else:
                    # Con lluvias
                    reply = ["Se anticipa que las lluvias comiencen pronto.",
                             "En este momento, hay un aviso de lluvia en la zona.",
                             "Las nubes en el horizonte indican que la lluvia es inminente.",
                             "Se registran alertas de lluvia para la zona."]

                return random.choice(reply)

            elif request == 'overall_climate':
                # Brinda el clima general
                reply = [f"En este momento tenemos un clima {self.current_accu.filtered_descrip}, con una temperatura de {self.current_accu.temp_metric} grados.",
                         f"En éstas horas el clima se presenta {self.current_accu.filtered_descrip}, la temperatura actual es de {self.current_accu.temp_metric} grados.",
                         f"El servicio reporta un clima {self.current_accu.filtered_descrip}, presentando una temperatura de {self.current_accu.temp_metric} grados."]

                print(random.choice(reply))
                #return random.choice(reply)


        # Para manejar eventos de Openweather
        elif 'openweather' in orchestrate_weather:
            if request == 'description':
                # Descripción
                reply = [f"El clima actualmente se encuentra {self.current_open.filtered_descrip}.",
                         f"En este momento, el clima está {self.current_open.filtered_descrip}.",
                         f"Las condiciones climáticas reflejan un entorno {self.current_open.filtered_descrip}.",
                         f"Acrualmente se observa un clima {self.current_open.filtered_descrip}."]

                return random.choice(reply)

            elif request == 'temperature':
                # Temperatura
                reply = [f"La temperatura actual es de {self.current_open.temp} grados.",
                         f"En este momento, la temperatura es de {self.current_open.temp} grados, la máxima esperada ronda los {self.current_open.temp_max}.",
                         f"Se registra una temperatura de {self.current_open.temp} grados en este momento.",
                         f"Según el reporte, estamos a {self.current_open.temp} grados y se espera una máxima de {self.current_open.temp_max} grados."]

                print(random.choice(reply))
                return random.choice(reply)

            elif request == 'wind':

                # Viento
                reply = [f"El viento es proveniente del {self.current_open.conversion_wind_deg}.",
                         f"La dirección del viento es del sector {self.current_open.conversion_wind_deg}.",
                         f"El viento sopla de la dirección {self.current_open.conversion_wind_deg}."]

                print(random.choice(reply))
                return random.choice(reply)


a = Current_Data()
a.weather_data_get(service='openweather', request='wind')

# Hasta ahora responde correctamente, falta añadir los comandos a la BD y cada uno si correspondiente servicio


