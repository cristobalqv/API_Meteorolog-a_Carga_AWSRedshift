# API Meteorología con carga de datos a AWS Redshift

### Proyecto que consiste en la creación de un script que extrae datos de una API pública con posterior creación y carga de datos en una tabla AWS Redshift.


### Los datos recopilados corresponden al pronóstico meteorológico para la ciudad de Santiago de Chile. Esta información fue extraída para los siguientes 5 días a contar de la fecha actual, con un intervalo de tiempo de 3 horas entre cada registro.

[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/santiago.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/santiago.png)


## Funcionamiento del proyecto
*1. Extracción de datos:*
Se extraen datos correspondientes a una serie de variables meteorológicas desde la API [Openweathermap](https://openweathermap.org/ "Openweathermap") y estos son almacenados en un objeto de tipo dataframe de pandas.


*2. Transformación de datos:*
Estos datos son procesados y transformados para su posterior carga a AWS Redshift. Específicamente, se procesan las columnas para modificar los tipos de datos a un formato compatible con Postgresql, en conjunto con creación de columnas de monitoreo (temporales) y creación de llave primaria compuesta.


*3. Carga de datos:*
Por último se verifica la existencia de la tabla (en caso de añadir una ciudad diferente a la predeterminada), se realiza una actualización de los datos para no generar información duplicada y se carga la información a AWS Redshift.


- Todo este proceso es orquestado mediante `Docker` y `Apache Airflow`. Docker nos permite trabajar con contenedores dentro de un entorno aislado, los cuales se pueden comunicar entre sí gracias a que forman parte de una red común, mientras que Airflow nos facilita ciertos servicios que facilitan tanto la visualización del estado de nuestro proceso ETL como la automatización del mismo


## Estructura del proyecto

Este repositorio está compuesto por 4 carpetas principales que contienen los archivos utilizados:

[`dags/`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/tree/main/dags "`dags/`")
- Contiene el archivo [dag.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/dags/dag.py "dag.py") el cual tiene como objetivo la ejecución diaria del proceso ETL en sí, el que le corresponde a la tarea *task_ETL_DAG*. Posterior a esta acción, la tarea *task_envio_mail* es responsable de enviar una notificación a un correo electrónico específico, informando si el proceso tuvo éxito o falló en algún momento. Esta tarea tiene en cuenta si las variables iniciales han sido cambiadas, y por lo tanto la información relacionada añadida a una nueva tabla en la base de datos.  

[`modulos/`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/tree/main/modulos "`modulos/`")
- Contiene el archivo [utils.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/utils.py "utils.py"), el que contiene las clases (y sus respectivos métodos y atributos) que van a ser llamados desde el script exterior *main_script.py* para poder ejecutar el proceso ETL. Por otro lado, el archivo [__init__.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/tree/main/modulos "__init__.py") no contiene información pero debe existir por defecto en la carpeta, para que scripts externos puedan acceder e interactuar con las clases y funciones presentes en *utils.py*. 

[`script`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/tree/main/script "`script`")
- En esta carpeta el archivo [main_script.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/script/main_script.py "main_script.py") es de donde se realiza el llamado a crear y ejecutar el código interno de *utils.py* correspondiente al proceso ETL. 

[`varios/`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/tree/main/varios "`varios/`")
- Contiene información variada en imágenes formato .png 


- [`docker-compose.yml`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/docker-compose.yml "`docker-compose.yml`"): Archivo con los servicios que son configurados para el funcionamiento del proceso. 
- [`Dockerfile`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/Dockerfile "`Dockerfile`"): Establece la versión de Python con la que levantaremos el proyecto
- [`requirements.txt`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/requirements.txt "`requirements.txt`"): Contiene las dependencias que serán utilizadas por los archivos de Python dentro del ambiente aislado de contenedores de Docker. 
- [`.gitignore`](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/.gitignore "`.gitignore`"): Contiene variables secretas que deben ser ignoradas al cargarlas al repositorio



### Actualización 14-09-2024 (Entrega final):

Consiste en generar un script para alertar via correo sobre el estado actual del proceso ETL. Para esto se hace uso del protocolo SMTP que permite enviar correos electrónicos entre ordenadores u otros dispositivos de forma segura. En primera instancia se codifica y añade un nuevo script que crea un "indicador_exito.txt" ([utils.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/utils.py "utils.py"), línea 174) que se va a generar únicamente si el proceso ETL tuvo éxito. Posteriormente agregamos en nuestro [dag.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/dags/dag.py "dag") las funciones "verificar_resultado" y "enviar_mail", las que interactuan y permiten el envío de una notificación a un correo específico si es que el procedimiento fue exitoso. Para poder generar este email necesitamos configurar y modificar ciertas variables que airflow genera al momento de crear y ejecutar los contenedores mediante Docker-compose. Estas variables a modificar corresponden principalmente a aquellas pertenecientes al [core], [celery] y [smpt] de Gmail. 
Finalmente se crea una nueva tarea "task_envio_email" que notifica al correo señalado el éxito o fallo en el proceso de ETL. Esta tarea está optimizada para alertar si hay cambios en el *main_script.py* respecto a las coordenadas y ciudad ingresada.


Las variables que hay que configurar manualmente y habilitar dentro del archivo "airflow.cfg" una vez ejecutado los contenedores son las siguientes:

```
[core]
executor = CeleryExecutor

[celery]
broker_url = redis://redis:6379/0
result_backend = db+postgresql://airflow:airflow@postgres/airflow

[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = tu_email@gmail.com
smtp_port = 587
smtp_password = tu_contraseña_de_gmail
smtp_mail_from = tu_email@gmail.com
```

Si bien hay algunas variables que ya se han definido anteriormente (celery) estas no están habilitadas en airflow.cfg, por lo que dejarlas deshabilitadas puede llevar a errores de ejecución.

Ejecución del dag de Airflow
[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/ejecucion_dag.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/ejecucion_dag.png)

Carga final de datos
[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/dbeaver.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/dbeaver.png)

Notificación de correo
[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/correo.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/correo.png)



### Actualización 01-09-2024 (Tercera pre-entrega):

Corresponde al proceso de automatización del script de ETL. Se trabajó con Docker en conjunto con Airflow, donde se creó un [Dockerfile](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/Dockerfile "Dockerfile") para la creación de una imagen con Airflow y Python y las dependencias necesarias para su correcta ejecución en Docker. Además se genera un archivo [docker-compose.yml](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/docker-compose.yml "docker-compose.yml") en el que se configuran los diferentes servicios necesarios para el funcionamiento del proceso en un entorno aislado de Docker. Posterior a esto, se genera un archivo [dag.py](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/dags/dag.py "dag") que se encarga de la llamada a un objeto de tipo PythonOperator, con una frecuencia de ejecución establecida. De esta forma, el proceso ETL es llamado por el dag y es ejecutado de manera diaria y automática.


### Consideraciones:
- Para poder hacer la conexión entre Python y AWS Redshift se utilizó  SQLAlchemy.  Es una herramienta que puede ser utilizada de diferentes formas, en este caso como conexión directa entre Python y SQL en un DataWarehouse como AWS Redshift.
Se utilizó el método anterior debido a su practicidad y simplicidad en la carga de datos a la nube.

- Coordenadas: `lat=-33.437` `lon=-70.650`  (Santiago de Chile)  
- *(estas coordenadas se pueden cambiar. Para esto se debe seguir el formato de grado decimal y con un límite de 3 cifras luego de la separación decimal. Además al modificarlas, se debe cambiar el nombre de la tabla por la nueva ciudad elegida, para que se cree una nueva tabla y no existan inconsistencias en la información. Seguir el formato "meteorologia_ciudad_codigopais"
Ejemplo: "meteorologia_londres_ig")*

- [Script principal](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/script/main_script.py "Script principal")

- [Clases y funciones utilizadas](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/utils.py "Clases y funciones utilizadas")
- [Librerías utilizadas](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/requirements.txt "Librerías utilizadas")

- [Variables](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/variables.png "Variables")

##### API utilizada: [Openweathermap](https://openweathermap.org/ "Openweathermap")
##### Documentación: https://openweathermap.org/forecast5

[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/openweathermap.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/openweathermap.png)


