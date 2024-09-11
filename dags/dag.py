from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

import smtplib
import os
import subprocess

load_dotenv()

#CREDENCIALES PARA ENVIAR NOTIFICACIONES DE CORREO 
sender_email = 'cjquirozv@gmail.com'
smtp_server = 'smtp.gmail.com'
smtp_port = 587
password_gmail = os.getenv('password_gmail')


def ejecutar_etl():
     try:
        result = subprocess.run(['python3', '/app/script/main_script.py'], check=True)
        print("Proceso ETL ejecutado correctamente")
     except subprocess.CalledProcessError as e:
        print(f"Error en la ejecución del script ETL: {e}")
        raise e


#AGREGO FUNCION PARA SABER SI EL PROCESO FUE EXITOSO O NO
def verificar_resultado():
     try:
          with open('/opt/airflow/logs/indicador_exito.txt', 'r') as f:
               status = f.read().strip()   #lee el archivo y elimina espacios para comparar posteriormente

               if status == 'success':
                    return 'El proceso ETL fue exitoso. Sus datos han sido cargados a AWS Redshift'
               else:
                    return 'El proceso ETL no se completó correctamente. Revise su código y vuelva a intentarlo nuevamente'
            
     except Exception as e:
          #si archivo indicador_exito.txt no existe, asume que el proceso ETL falló
          return f'Archivo indicador_exito.txt no existe, no fue posible subir los datos a AWS Redshift. {e}'
     

def enviar_mail():
     try:
          subject = 'Notificación proceso ETL'
          body_text = verificar_resultado()

          msg = MIMEMultipart()   #objeto de tipo MIMEMultipart. Para crear y manejar correos que pueden contener diferentes partes (texto, imágenes, archivos adjuntos, etc.)
          msg['From'] = sender_email
          msg['To'] = sender_email
          msg['Subject'] = subject
          msg.attach(MIMEText(body_text, 'plain'))   #con esto se adjunta el cuerpo del mensaje en formato plano 

          #abrimos conexión con el servidor SMTP de Gmail
          with smtplib.SMTP(smtp_server, smtp_port) as server:
               server.starttls()       #sesión segura usando TLS
               server.login(sender_email, password_gmail)
               server.send_message(msg)
               print('El email fue enviado correctamente.')
               
     except Exception as e:
          print(f'Hubo un error al enviar el correo. {e}')
          


default_args = {'owner': 'cristobalqv',
                'retries': 5,
                'retry_delay': timedelta(minutes=3)}

with DAG(default_args=default_args,
         dag_id='etl_meterorologia',
         description='DAG para realizar proceso ETL. extracción desde API, transformación y carga a AWS',
         start_date=datetime(2024,8,27),
         schedule_interval='@daily',
         catchup=False) as dag:
    

     task_ETL_DAG = PythonOperator(
        task_id='ejecutar_etl',
        python_callable=ejecutar_etl)
     

     task_envio_mail = PythonOperator(
          task_id = 'envio_correo',
          python_callable = enviar_mail)
     
     task_ETL_DAG >> task_envio_mail