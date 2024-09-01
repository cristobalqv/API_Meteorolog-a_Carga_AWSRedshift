# API Meteorología con carga de datos a AWS Redshift

### Proyecto que consiste en la creación de un script que extrae datos de una API pública con posterior creación y carga de datos en una tabla AWS Redshift.


### Los datos recopilados corresponden al pronóstico meteorológico para la ciudad de Santiago de Chile. Esta información fue extraída para los siguientes 5 días a contar de la fecha actual, con un intervalo de tiempo de 3 horas entre cada registro.

[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/santiago.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/santiago.png)


Consideraciones:
- Para poder hacer la conexión entre Python y AWS Redshift se utilizó  SQLAlchemy.  Es una herramienta que puede ser utilizada de diferentes formas, en este caso como conexión directa entre Python y SQL en un DataWarehouse como AWS Redshift.
Se utilizó el método anterior debido a su practicidad y simplicidad en la carga de datos a la nube.

- Coordenadas: lat=-33.437   lon=-70.650

- [Script principal](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/script/main_script.py "Script principal")

- [Clases y funciones utilizadas](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/utils.py "Clases y funciones utilizadas")
- [Librerías utilizadas](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/modulos/requirements.txt "Librerías utilizadas")

- [Variables](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/variables.png "Variables")

##### API utilizada: [Openweathermap](https://openweathermap.org/ "Openweathermap")
##### Documentación: https://openweathermap.org/forecast5

[![](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/openweathermap.png)](https://github.com/cristobalqv/API_Meteorolog-a_Carga_AWSRedshift/blob/main/varios/openweathermap.png)


