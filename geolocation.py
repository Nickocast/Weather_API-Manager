import sqlite3
from pathlib import Path
from weather_utils import GetData_DB

import requests


# ///////////////////////////////////   ACCUWEATHER-GEOLOCATION    /////////////////////////////////////////////////// #
class Accuweather_Geolocation(GetData_DB):

    def __init__(self):

        # Se obtiene la ciudad y la key correspondientes del servicio desde la base de datos:
        self.apikey = self.get_apikey('Accuweather')
        # Agregar logging

    def accu_search_city(self):  # 1

        # Obtiene los datos de la ciudad por medio de la api del servicio:
        try:
            url = "http://dataservice.accuweather.com/locations/v1/cities/autocomplete"
            parameters = {
                'apikey': self.apikey,
                'q': self.get_city_config(),
                'language': 'es'
            }

            reply = requests.get(url, params=parameters)

            if reply.status_code == 200:
                data = reply.json()
                print("Accuweather city-data: ", data)

                print("Accuweather: Se obtuvieron los datos correctamente")
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

        except requests.RequestException as e:
            print("Error: ", e)

    def accu_update_or_insert_city_data(self):  # 2
        """Metodo que se encarga de obtener los datos necesarios y almacenarlos en la BD."""
        data = self.accu_search_city()

        if data is not None:

            # Selecciona los datos relevantes que se necesitan extraer:
            city_key = data[0]['Key']  # Clave de ubicación
            city_name = data[0]['LocalizedName']  # Nombre de la ciudad

            # Localiza la carpeta raíz donde se encuentra la Base de Datos:
            base_dir = Path(__file__).resolve().parent.parent.parent
            path_db = base_dir / 'aurora_db.db'

            # Conecta a la BD:
            conn = sqlite3.connect(path_db)
            cursor = conn.cursor()

            try:
                # Verifica si la fila ya existe
                cursor.execute('SELECT api_name FROM geolocation WHERE geo_id = ?', (1,))
                result = cursor.fetchone()

                if result:

                    # Actualiza solo las columnas necesarias, sin tocar `api_name`
                    cursor.execute(
                        '''
                        UPDATE geolocation 
                        SET city_key = ?, city_name = ? 
                        WHERE geo_id = ?
                        ''',
                        (city_key, city_name, 1)
                    )

                    print("Datos de la ciudad actualizados correctamente.")
                else:
                    # Inserta los datos correspondientes en la BD
                    cursor.execute('''
                    INSERT INTO geolocation (city_key, city_name) VALUES (?, ?)
                    ''', (city_key, city_name))

                    print("Datos guardados correctamente.")

                conn.commit()

            except sqlite3.Error as e:
                print("Los datos no se han podido guardar correctamente, error: ", e)

            finally:
                # Cierra conexión a la BD
                cursor.close()
                conn.close()

        else:
            print("Solicitudes excedidas. Servicio desconectado.")


# ///////////////////////////////////   OPENWEATHER-GEOLOCATION    /////////////////////////////////////////////////// #

class Openweather_Geolocation(GetData_DB):

    def __init__(self):
        # Se obtiene la ciudad y la key correspondientes del servicio desde la base de datos:
        self.apikey = self.get_apikey('Openweather')
        # Agregar logging

    def open_search_city(self):  # 1

        # Obtiene los datos de la ciudad por medio de la api del servicio:
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={self.get_city_config()}&limit=5&appid={self.apikey}"

            reply = requests.get(url)

            if reply.status_code == 200:
                data = reply.json()

                print("Openweather: Se obtuvieron los datos correctamente")
                return data

            elif reply.status_code == 401:
                print("401 - Unauthorized: clave inválida.")

            elif reply.status_code == 404:
                print("404 - Not Found: no existe el recurso solicitado.")

            elif reply.status_code == 429:
                print("Too Many Requests: Límite de llamadas superado.")

            else:
                print("Openweather: Error al obtener los datos del servidor.")

        except requests.RequestException as e:
            print("Error: ", e)

    def open_update_or_insert_city_data(self):  # 2
        """Metodo que se encarga de obtener los datos necesarios y almacenarlos en la BD."""

        data = self.open_search_city()

        # Selecciona los datos relevantes que se necesitan extraer:
        city_name = data[0]['name']
        latitude = data[0]['lat']
        longitude = data[0]['lon']
        print(f"/////////city: {city_name}, lat: {latitude}, longitud: {longitude}")

        # Localiza la carpeta raíz donde se encuentra la Base de Datos:
        base_dir = Path(__file__).resolve().parent.parent.parent
        path_db = base_dir / 'aurora_db.db'

        # Conecta a la BD:
        conn = sqlite3.connect(path_db)
        cursor = conn.cursor()

        try:

            # Verifica si la fila ya existe
            cursor.execute('SELECT api_name FROM geolocation WHERE geo_id = ?', (2,))
            result = cursor.fetchone()

            if result:

                # Actualiza solo las columnas necesarias, sin tocar `api_name`
                cursor.execute(
                    '''
                    UPDATE geolocation 
                    SET latitude = ?, longitude = ?, city_name = ? 
                    WHERE geo_id = ?
                    ''',
                    (latitude, longitude, city_name, 2)
                )

                conn.commit()
                print("SAVE DB: Datos de la ciudad actualizados correctamente.")

            else:
                # Inserta los datos correspondientes en la BD
                cursor.execute('''
                                    INSERT INTO geolocation (latitude, longitude, city_name) VALUES (?, ?, ?)
                                ''', (latitude, longitude, city_name))

                conn.commit()
                print("SAVE DB: Datos guardados correctamente.")

        except sqlite3.Error as e:
            print("Los datos no se han podido guardar correctamente, error: ", e)

        finally:
            # Cierra conexión a la BD
            cursor.close()
            conn.close()


# Clase que contiene el método de verificación de ciudad para obtener los datos-----------------------------------------
class Matcher(Openweather_Geolocation, Accuweather_Geolocation, GetData_DB):

    def __init__(self):
        # Variables de almacenamiento:
        self.api_accu = ''
        self.city_key = ''
        self.api_open = ''
        self.lat = ''
        self.lon = ''

    def verify_city_match(self, service):  # Script: current_weather.py # 1
        """Método que se encarga de la verificación de la ciudad de configuración y de la api sean iguales,
           para la devolución correcta de datos."""
        # Se obtiene los datos de las ciudades de las api's almacenados en la base de datos
        self.get_all_api_data()

        if service == 'Accuweather':

            # Se realiza la verificación para Accuweather:
            if self.get_city_config() == self.accu_city_api_data:
                return True

            elif self.get_city_config() != self.accu_city_api_data:
                self.accu_update_or_insert_city_data()
                print("MATCHER: Datos actualizados de Accuweather actualizados correctamente.")
                return True

        elif service == 'Openweather':
            # Se realiza la verificación para Openweather:
            if self.get_city_config() == self.open_city_api_data:
                return True

            elif self.get_city_config() != self.open_city_api_data:
                self.open_update_or_insert_city_data()
                print("MATCHER: Datos actualizados de Openweather actualizados correctamente.")
                return True

        else:
            print("Surgió un problema con la obtención de datos en Matcher.")

    def get_all_api_data(self):  # 2
        """Obtiene toda la inforamción almacenada de las api y las ordena en las variables necesarias."""

        # Obtiene los datos de la tabla de geolocalización:
        data = self.get_city_api_all_data()

        # Almaceno los datos correspondientes en cada variable global para su uso:
        if data:
            # Accuweather info:
            self.api_accu = data[0][1]
            self.city_key = int(data[0][2])

            # Openweather info:
            self.api_open = data[0][1]
            self.lat = data[1][3]
            self.lon = data[1][4]

            # Ciudad almacenada de las api:
            self.accu_city_api_data = data[0][5]
            self.open_city_api_data = data[1][5]

        return self.api_accu, self.city_key, self.api_open, self.lat, self.lon, self.accu_city_api_data, self.open_city_api_data
