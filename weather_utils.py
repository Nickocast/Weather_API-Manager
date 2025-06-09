import json
import sqlite3
from pathlib import Path
import datetime

'''
Módulo de uso general para el paquete de weaather_service que contiene funciones de obtención de datos
necesarios para el correcto funcionamiento de la busqueda y geolocaclización de posición geográfica.
'''

class GetData_DB:

    def get_base_dir(self):  # Script: geolocation.py, current_weather.py
        """Localiza el directorio raíz de la ubicación de la Base de Datos."""

        base_dir = Path(__file__).resolve().parent.parent.parent
        path_db = base_dir / 'aurora_db.db'
        return path_db

    def get_apikey(self, service):  # Script: geolocation.py, current_weather.py
        """Método que se encarga de obtener la api correspondiente de la BD."""

        # Obtengo la ubicación exacta de la BD:
        path_db = self.get_base_dir()

        try:
            conn = sqlite3.connect(path_db)
            cursor = conn.cursor()

            sql = f"SELECT key FROM apis WHERE empresa= '{service}'"
            cursor.execute(sql)

            key = cursor.fetchone()  # Obteniene solo la apikey de ese servicio

            if key:
                key = key[0]  # Extrae de la tupla solo el contenido y lo muestra(excluye parentesis y comillas).
                return key
            else:
                print("No se encontró la apikey de la empresa solicidata.")


        except sqlite3.Error as e:

            print("Error al obtener Apikey: ", e)

        finally:
            cursor.close()
            conn.close()

    def get_city_config(self):  # Script: geolocation.py, current_weather.py
        """Método que se encarga de obtener la ciudad almacenada en la BD."""

        # Obtiene la ubicación exacta de la BD:
        path_db = self.get_base_dir()

        conn = sqlite3.connect(path_db)
        cursor = conn.cursor()

        try:
            sql = f"SELECT city FROM configuration"
            cursor.execute(sql)

            city = cursor.fetchone()  # Obteniene solo la ciudad de la configuración de usuario

            if city:
                city = city[0]  # Extrae de la tupla solo el contenido y lo muestra(excluye parentesis y comillas).
                return city
            else:
                print("No se encontró el nombre de la localización en la base de datos.")


        except sqlite3.Error as e:

            print("Error al obtener la localización en la base de datos: ", e)


        finally:
            cursor.close()
            conn.close()

    def get_city_api_all_data(self):  # Script: current_weather.py
        """Método que se encarga de obtener todos los datos desde la BD para el uso de las apis de clima."""

        # Obtiene la ubicación exacta de la BD:
        path_db = self.get_base_dir()

        try:
            conn = sqlite3.connect(path_db)
            cursor = conn.cursor()

            sql = f"SELECT * FROM geolocation"
            cursor.execute(sql)

            city_data = cursor.fetchall()  # Consulta el contenido de toda la tabla.
            return city_data

        except sqlite3.Error as e:

            print("Error al obtener Apikey: ", e)

        finally:
            cursor.close()
            conn.close()

    def dictionary_description(self, service, condition):  # 3
        """Diccionario de descripciones de la api en lenguaje más comprensible y adaptado."""
        path = Path(r'C:\Users\Be-Nicko\Documents\PycharmProjects\Asistente2G\services\weather_service\descriptions.json')

        # Lee el json donde contiene las descripciones modificadas
        with open(path, 'r', encoding="utf-8") as file:
            descriptions = json.load(file)

        if service == 'Openweather':
            # Para Openweather
            # Accede al diccionario dentro de la lista
            conditions = descriptions["weather_data"][0]["conditions"]

            if condition in conditions:
                return conditions[condition]

        elif service == 'Accuweather':
            # Para Accuweather
            # Acceder al diccionario dentro de la lista
            conditions = descriptions["weather_data"][1]["conditions"]

            # Verificar si la clave existe en las condiciones
            if str(condition) in conditions:
                return conditions[str(condition)]

        # Si no se encuentra
        return "Descripción no disponible"

    def conversion_time(self, sunrise, sunset):
        """Función de conversión de formato de tiempo."""

        self.sunrise = None
        self.sunset = None

        # Convertir las marcas de tiempo a objetos datetime
        sunrise = datetime.datetime.fromtimestamp(sunrise)
        sunset = datetime.datetime.fromtimestamp(sunset)

        # Formatear la salida en un formato legible
        self.sunrise_formatted = sunrise.strftime('%H:%M')  # Formato: Horas:Minutos
        self.sunset_formatted = sunset.strftime('%H:%M')

        return self.sunrise_formatted, self.sunset_formatted

    def conversion_metrics(self, number):
        """Función de conversión de valores."""

        # Metrós a Kilómertos
        conversion = number / 1000

        return conversion

    def wind_convert(self, wind_deg):
        """Método que convierte las variables en forma comprensible para la persona."""

        # Calcular la dirección del viento en 8 puntos cardinales
        directions = [
            "Norte",    # 0°
            "Noreste",  # 45°
            "Este",     # 90°
            "Sureste",  # 135°
            "Sur",      # 180°
            "Suroeste", # 225°
            "Oeste",    # 270°
            "Noroeste"  # 315°
        ]

        direction = int((wind_deg + 22.5) % 360 / 45)

        wind_direction = directions[direction]
        return wind_direction
