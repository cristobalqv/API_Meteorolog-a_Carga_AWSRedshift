import os
import pandas as pd
from dotenv import load_dotenv
from modulos.utils import ConexionAPIDescargaJSON, RedshiftManager

load_dotenv()     #carga variables ambientales del archivo .env

#VARIABLES A CONSIDERAR
credenciales_redshift = {
    'redshift_user': os.getenv('redshift_user'),
    'redshift_pass': os.getenv('redshift_pass'),
    'redshift_host': os.getenv('redshift_host'),
    'redshift_port': os.getenv('redshift_port'),
    'redshift_database': os.getenv('redshift_database') 
}

schema = 'cjquirozv_coderhouse'
api_key = os.getenv('api_key')


#-------VARIABLES--------

latitud = 40.5
longitud = -3.666
nombre_tabla = 'meteorología_españa_ES'

#guardo las coordenadas para incluirlas posteriormente en el email_task del dag 
with open('/opt/airflow/logs/coordenadas.txt', 'w') as f:
    f.write(f'Latitud= {latitud}, Longitud= {longitud}, Nombre tabla: {nombre_tabla}')



url_base = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitud}&lon={longitud}&appid={api_key}'




#EJECUCIÓN
if __name__=="__main__":

    conexion = ConexionAPIDescargaJSON(url_base)
    conexion.conectar_API_devolver_json()    #archivo sin parsear de la respuesta del servidor que se guarda en el objeto conexion.response_json
    conexion.convertir_json_a_dataframe()    #retornará self.df que será guardado en el atributo conexion.df
    df = conexion.procesar_dataframe()            

    redshift = RedshiftManager(credenciales_redshift, schema)
    redshift.crear_motor_conexion_redshift()

    # agrego un condicional en caso de que las coordenadas y nombre cambien y tenga que generar una nueva tabla. Si no existe se crea
    if not redshift.verificar_si_tabla_existe(nombre_tabla):
        redshift.crear_nueva_tabla(nombre_tabla)
        redshift.actualizar_fechas_horas(df, nombre_tabla)
        redshift.cargar_nuevos_datos(df, nombre_tabla)
        redshift.cerrar_conexion_redshift()

    redshift.actualizar_fechas_horas(df, nombre_tabla)
    redshift.cargar_datos_redshift(df, nombre_tabla)
    # redshift.modificar_columnas_crear_llave_compuesta('meteorología_santiago_cl')  #Esta parte del codigo la omitimos porque ya la llamamos, modificamos y creamos
    redshift.cerrar_conexion_redshift()