import requests
import psycopg2
import json
import pandas as pd

from sqlalchemy import create_engine, text
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
                    diccionario['fecha'].append(elemento['dt_txt'])
                    diccionario['hora'].append(elemento['dt_txt'])
                    diccionario['temperatura'].append(elemento['main']['temp'])
                    diccionario['t_sensacion_termica'].append(elemento['main']['feels_like'])
                    diccionario['t_minima'].append(elemento['main']['temp_min'])
                    diccionario['t_maxima'].append(elemento['main']['temp_max'])
                    diccionario['condicion'].append(elemento['weather'][0]['main'])
                    diccionario['descripcion'].append(elemento['weather'][0]['description'])
                    diccionario['veloc_viento'].append(elemento['wind']['speed'])
                    diccionario['%_humedad'].append(elemento['main']['humidity'])
                    diccionario['probabilidad_precip'].append(elemento['pop'])
                    diccionario['precip_ultimas_3h(mm)'].append(elemento.get('rain', {}).get('3h', 0))  #como ciertos diccionarios 
                                                    # no tienen la clave "rain" (casos en que no llueve), se maneja de esta forma.
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
    

    def procesar_dataframe(self):
        if self.df is not None:
            try:
                self.df['fecha'] = self.df['fecha'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date())
                self.df['hora'] = self.df['hora'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").time())
                self.df['temperatura'] = self.df['temperatura'].apply(lambda x: round(float(x)-273.15, 1)) 
                self.df['t_sensacion_termica'] = self.df['t_sensacion_termica'].apply(lambda x: round(float(x)-273.15, 1))
                self.df['t_minima'] = self.df['t_minima'].apply(lambda x: round(float(x)-273.15, 1))
                self.df['t_maxima'] = self.df['t_maxima'].apply(lambda x: round(float(x)-273.15, 1))
                self.df['veloc_viento'] = self.df['veloc_viento'].apply(lambda x: round(float(x)*3.6)) 
                self.df['probabilidad_precip'] = self.df['probabilidad_precip'].apply(lambda x: x*100)
                self.df['precip_ultimas_3h(mm)'] =  self.df['precip_ultimas_3h(mm)'].apply(lambda x: float(x))
            except Exception as e:
                print(f'Ocurrió un error al procesar el dataframe: {e}')

            return self.df       #es necesario retornar el df completo nuevamente ya que trabajaremos con él fuera de la clase
        else:
            print('No hay dataframe para procesar')
            return self.df





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


    #SEGUNDA ENTREGA: Crear lista de claves primaria compuesta que involucre fecha y hora. Al no tener una clave primaria que 
    # identifique a un registro como único, generamos una clave primaria compuesta entre fecha y hora. Esto nos da 2 ventajas: 
    # identificar cada registro dentro del dataframe como único, y también nos da una guía para actualizar ciertos registros 
    # que podrían duplicarse. De esta forma, al actualizar nuestra tabla con nuevos registros que posiblemente sean duplicados 
    # en fecha y hora, primero se van a eliminar los registros que corresponden a la misma fecha y hora, pero que fueron 
    # extraídos en primera instancia. Así se pueden reemplazar adecuadamente los registros que presentan la misma fecha y 
    # hora al ejecutar el script.

    def actualizar_fechas_horas(self, dataframe, nombretabla):   #toma el dataframe, compara los registros con los de la tabla
        # en la base de datos, y elimina aquellos de la base de datos que coinciden con los nuevos
        if self.conexion is not None:
            try:
                fechas_horas = dataframe[['fecha', 'hora']].values.tolist()  #Esto va a generar una lista de listas a partir 
                # del dataframe que quiero insertar, y que contendrá la fecha y hora de los registros nuevos
                for fecha, hora in fechas_horas:
                    query_eliminar = f'''DELETE FROM {nombretabla} WHERE fecha = '{fecha}' AND hora = '{hora}';'''     
                    # elimina cada registro de hora y fecha  creado antes del dataframe actual, para que pueda ser actualizado 
                    # por los registros coincidentes del nuevo dataframe
                    self.conexion.execute(text(query_eliminar))
                print('Se actualizó correctamente la información')
            except Exception as e:
                print(f'Ocurrió un error al actualizar los registros de hora y fecha: {e}')


    def cargar_datos_redshift(self, dataframe, nombretabla):  
        if self.conexion is not None:
            try: 
                tabla = dataframe.to_sql(nombretabla, con=self.conexion, schema=self.schema, if_exists='append', index=False)
                

                #agregar 2 columnas temporales con fecha y hora de carga
                self.crear_columnas_temporales(nombretabla)                  


                print(f'Dataframe cargado con éxito en AWS Redshift') 

            except Exception as e:
                print(f'Error al cargar dataframe a AWS Redshift: {e}')
        else:
            print("No hay conexión creada con AWS Redshift. Intenta establecer una conexión")



    #Debemos gestionar la lógica para cuando agregamos una nueva ciudad, por lo tanto una nueva tabla

    #verificar si tabla existe
    def verificar_si_tabla_existe(self, nombretabla):
        if self.conexion is not None:
            query = f"""SELECT EXISTS 
                        (SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_schema = '{self.schema}' AND table_name = '{nombretabla}');"""
            resultado = self.conexion.execute(text(query)).fetchone()
            return resultado[0]   #Si la tabla existe va a retornar True. Si no existe, False


    # crear nueva tabla en redshift
    def crear_nueva_tabla(self, nombretabla: str):
        if self.conexion is not None:
            try:
                query_creacion_tabla = f"""CREATE TABLE IF NOT EXISTS {self.schema}.{nombretabla} (
                fecha DATE,
                hora TIME,
                temperatura FLOAT,
                t_sensacion_termica FLOAT,
                t_minima FLOAT,
                t_maxima FLOAT,
                condicion VARCHAR(256),
                descripcion VARCHAR (256),
                veloc_viento INT,
                %_humedad INT,
                probabilidad_precip FLOAT,
                precip_ultimas_3h FLOAT,
                fecha_carga DATE DEFAULT CURRENT_DATE NOT NULL,
                hora_carga VARCHAR(8) DEFAULT TO_CHAR(CURRENT_TIMESTAMP, 'HH24:MI:SS') NOT NULL,
                PRIMARY KEY (fecha, hora));"""

                self.conexion.execute(text(query_creacion_tabla))
                print('Nueva tabla creada con éxito en AWS Redshift')

            except Exception as e:
                print(f'Hubo un error al crear la tabla: {e}')


    def cargar_nuevos_datos(self, dataframe, nombretabla):
            if self.conexion is not None:
                try: 
                    tabla = dataframe.to_sql(nombretabla, con=self.conexion, schema=self.schema, if_exists='append', index=False)

                    #agregar 2 columnas temporales con fecha y hora de carga
                    # self.crear_columnas_temporales(nombretabla)               
                    print(f'Dataframe cargado con éxito en AWS Redshift')

                except Exception as e:
                    print(f'Error al cargar dataframe a AWS Redshift: {e}')
            else:
                print("No hay conexión creada con AWS Redshift. Intenta establecer una conexión")


    #Cerrar conexión de AWS Redshift
    def cerrar_conexion_redshift(self):
        if self.conexion:
            try:
                self.conexion.close()
                print('Conexión cerrada.')
                return self.conexion
            except Exception as e:
                print(f'ocurrió un error al cerrar la conexión: {e}')
        else:
            print('No hay conexión abierta. Intenta abrir una conexión nueva')

