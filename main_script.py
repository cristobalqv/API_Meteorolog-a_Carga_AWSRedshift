import os
import pandas as pd
from dotenv import load_dotenv
from paquetes.utils import ConexionAPIDescargaJSON, RedshiftManager

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
url_base = f'https://api.openweathermap.org/data/2.5/forecast?lat=-33.437&lon=-70.650&appid={api_key}'


#EJECUCIÓN
conexion1 = ConexionAPIDescargaJSON(url_base)
conexion1.conectar_API_devolver_json()
df = conexion1.convertir_json_a_dataframe()

redshift = RedshiftManager(credenciales_redshift, schema)
redshift.crear_motor_conexion_redshift()
redshift.cargar_datos_redshift(df, 'meteorología_santiago_cl')
redshift.cerrar_conexion_redshift

