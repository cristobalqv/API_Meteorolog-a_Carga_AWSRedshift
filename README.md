# API Meteorología con carga de datos a AWS Redshift

### Proyecto que consiste en la creación de un script que extrae datos de una API pública con posterior creación y carga de datos en una tabla AWS Redshift.


### Los datos recopilados corresponden al pronóstico meteorológico para la ciudad de Santiago de Chile. Esta información fue extraída para los siguientes 5 días a contar de la fecha actual, con un intervalo de tiempo de 3 horas entre cada registro.

[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/santiago.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/santiago.png)

**__________________________________________________________________________**
### Actualización 11-09-2024 (Entrega final):

Consiste en generar un script para alertar via correo sobre el estado actual del proceso ETL. Para esto se hace uso del protocolo SMTP que permite enviar correos electrónicos entre ordenadores u otros dispositivos de forma segura. En primera instancia se codifica y añade un nuevo script que crea un "indicador_exito.txt" ([utils.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/utils.py "utils.py"), línea 174) que se va a generar únicamente si el proceso ETL tuvo éxito. Posteriormente agregamos en nuestro [dag.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/dags/dag.py "dag") las funciones "verificar_resultado" y "enviar_mail", las que interactuan y permiten el envío de una notificación a un correo específico si es que el procedimiento fue exitoso. Para poder generar este email necesitamos configurar y modificar ciertas variables que airflow genera al momento de crear y ejecutar los contenedores mediante Docker-compose. Estas variables a modificar corresponden principalmente a aquellas pertenecientes al [core], [celery] y [smpt] de Gmail. 
Finalmente se crea una nueva tarea "task_envio_email" que notifica al correo señalado el éxito o fallo en el proceso de ETL.
Las variables que hay que configurar manualmente y habilitar dentro del archivo "airflow.cfg" una vez ejecutado los contenedores son las siguientes:

- [core]
- executor = CeleryExecutor
- [celery]
- broker_url = redis://redis:6379/0
- result_backend = db+postgresql://airflow:airflow@postgres/airflow
- [smtp]
- smtp_host = smtp.gmail.com
- smtp_starttls = True
- smtp_ssl = False
- smtp_user = tu_email@gmail.com
- smtp_port = 587
- smtp_password = tu_contraseña_de_gmail
- smtp_mail_from = tu_email@gmail.com

Si bien hay algunas variables que ya se han definido anteriormente (celery) estas no están habilitadas en airflow.cfg, por lo que dejarlas deshabilitadas puede llevar a errores de ejecución.

Ejecución del dag de Airflow
[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/ejecucion_dag.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/ejecucion_dag.png)

Carga final de datos
[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/dbeaver.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/dbeaver.png)

Notificación de correo
[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/correo.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/correo.png)

**__________________________________________________________________________**
### Actualización 01-09-2024 (Tercera pre-entrega):

Corresponde al proceso de automatización del script de ETL. Se trabajó con Docker en conjunto con Airflow, donde se creó un [Dockerfile](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/Dockerfile "Dockerfile") para la creación de una imagen con Airflow y Python y las dependencias necesarias para su correcta ejecución en Docker. Además se genera un archivo [docker-compose.yml](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/docker-compose.yml "docker-compose.yml") en el que se configuran los diferentes servicios necesarios para el funcionamiento del proceso en un entorno aislado de Docker. Posterior a esto, se genera un archivo [dag.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/dags/dag.py "dag") que se encarga de la llamada a un objeto de tipo PythonOperator, con una frecuencia de ejecución establecida. De esta forma, el proceso ETL es llamado por el dag y es ejecutado de manera diaria y automática.

**__________________________________________________________________________**

Consideraciones:
- Para poder hacer la conexión entre Python y AWS Redshift se utilizó  SQLAlchemy.  Es una herramienta que puede ser utilizada de diferentes formas, en este caso como conexión directa entre Python y SQL en un DataWarehouse como AWS Redshift.
Se utilizó el método anterior debido a su practicidad y simplicidad en la carga de datos a la nube.

- Coordenadas: lat=-33.437   lon=-70.650  

- [Script principal](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/script/main_script.py "Script principal")

- [Clases y funciones utilizadas](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/utils.py "Clases y funciones utilizadas")
- [Librerías utilizadas](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/requirements.txt "Librerías utilizadas")

- [Variables](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/variables.png "Variables")

##### API utilizada: [Openweathermap](https://openweathermap.org/ "Openweathermap")
##### Documentación: https://openweathermap.org/forecast5

[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/openweathermap.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/openweathermap.png)


