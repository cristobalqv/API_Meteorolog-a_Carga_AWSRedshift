import requests
import psycopg2
import json
import pandas as pd

from sqlalchemy import create_engine
from datetime import datetime


#Clase para manejar conexion a la API y descarga de información
class ConexionAPIDescargaJSON():
    def __init__(self, url):
        self.url = url
        self.response_json = None
        self.df = None
        
        
    #Conectar con la API y devuelve un archivo en JSON parseado
    def conectar_API_devolver_json(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                self.response_json = response.json()
                print('Conexión exitosa a la API. Archivo JSON listo para ser procesado')
                return self.response_json
        except Exception as e:  
            print(f'No se pudo establecer la conexión con el servidor. Sugerencia: Revisar url y parámetros utilizados. Error {response.status_code}: {e}')
            return 
        


    #Recibe un archivo JSON devuelto por la API y lo convierte en un dataframe de pandas.
    #La transformación de ciertos metadatos a un formato específico ocurre en la misma iteración y agregación a las claves(columnas) del diccionario. De esta forma se pueden transformar posteriormente los datos, pero en menor medida
    def convertir_json_a_dataframe(self):
        diccionario = {'fecha': [], 
                        'hora': [],
                        'temperatura': [],
                        't_sensacion_termica': [],
                        't_minima': [],
                        't_maxima': [],
                        'condicion': [],
                        'descripcion': [],
                        'veloc_viento': [],
                        '%_humedad': [],
                        'probabilidad_precip': [],
                        'precip_ultimas_3h(mm)': []
                        }
        if self.response_json is not None:
            for elemento in self.response_json['list']:
                try:
                    diccionario['fecha'].append(datetime.strptime(elemento['dt_txt'], "%Y-%m-%d %H:%M:%S").date())
                    diccionario['hora'].append(datetime.strptime(elemento['dt_txt'], "%Y-%m-%d %H:%M:%S").time())
                    diccionario['temperatura'].append(round(float(elemento['main']['temp']) -273.15, 1))
                    diccionario['t_sensacion_termica'].append(round(float(elemento['main']['feels_like']) -273.15, 1))
                    diccionario['t_minima'].append(round(float(elemento['main']['temp_min']) -273.15, 1))
                    diccionario['t_maxima'].append(round(float(elemento['main']['temp_max']) -273.15, 1))
                    diccionario['condicion'].append(elemento['weather'][0]['main'])
                    diccionario['descripcion'].append(elemento['weather'][0]['description'])
                    diccionario['veloc_viento'].append(round(float(elemento['wind']['speed']) *3.6))
                    diccionario['%_humedad'].append(float(elemento['main']['humidity']))
                    diccionario['probabilidad_precip'].append(elemento['pop'] *100)
                    diccionario['precip_ultimas_3h(mm)'].append(float(elemento.get('rain', {}).get('3h', 0)))   #como ciertos diccionarios no tienen la clave "rain" (casos en que no llueve), se maneja de esta forma.
                except Exception as e:
                    print(f'Ocurrió un error al consolidar datos al diccionario: {e}')
            print('Carga de datos al diccionario exitosa')
            
            try:
                self.df = pd.DataFrame(diccionario)
            except Exception as e:
                print(f'Ocurrió un error al convertir a dataframe el diccionario: {e}')
                self.df = pd.DataFrame()    #Genero un dataframe incluso si hay error

            return self.df
        else:
            raise ValueError("No hay archivo JSON para procesar aún")

    

#Clase para manejar conexión y carga a AWS Redshift
class RedshiftManager():
    def __init__(self, credenciales: dict, schema: str):
        self.credenciales = credenciales
        self.schema = schema
        self.conexion = None
        


    #Se crea un engine que conecta a redshift medianate una url con formato: "dialect+driver://username:password@host:port/database"
    def crear_motor_conexion_redshift(self):
        user = self.credenciales.get('redshift_user')
        password = self.credenciales.get('redshift_pass')
        host = self.credenciales.get('redshift_host')
        port = self.credenciales.get('redshift_port')
        database = self.credenciales.get('redshift_database')

        try:
            engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
            print('Motor creado exitosamente')
            try:
                self.conexion = engine.connect()
                #ejecutamos un query aleatorio para ver si la conexión está estable
                prueba = self.conexion.execute('SELECT 1;')
                if prueba:
                    print('Conectado a AWS Redshift con éxito')
                    return self.conexion
                else:
                    print('Conectado a AWS pero con problemas con ejecución de querys')
                    return
            except Exception as e:
                print(f'Fallo al tratar de conectar a AWS Redshift. {e}')
        except Exception as e:
            print(f'Error al intentar crear el motor: {e}')  



    #Carga del dataframe a AWS Redshift
    def cargar_datos_redshift(self, dataframe, nombretabla):
        if self.conexion is not None:
            try: 
                tabla = dataframe.to_sql(nombretabla, con=self.conexion, schema=self.schema, if_exists='replace', index=False)
                print(f'Dataframe cargado con éxito en AWS Redshift')
            except Exception as e:
                print(f'Error al cargar dataframe a AWS Redshift: {e}')
        else:
            print("No hay conexión creada con AWS Redshift. Intenta establecer una conexión")



    #Cerrar conexión de AWS Redshift
    def cerrar_conexion_redshift(self):
        if self.conexion:
            self.conexion.dispose()
            print('Conexión cerrada.')
            return self.conexion
        else:
            print('No hay conexión abierta. Intenta abrir una conexión nueva')