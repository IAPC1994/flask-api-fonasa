# FONASA FLASK API

## Requisitos
1. Tener Python instalado
2. Tener una conexión MySQL para ejecutar script ubicado en la carpeta assets 
3. Colocar usuario y password en la config de la app.
4. Tener el puerto 4000 disponible (Sino, cambiar puerto en archivo app.py al final)

## Instalar
1. Crear el ambiente virtual de python en la carpeta con `python -m virtualenv venv`
2. Activar el entorno virtual con `./venv/Scripts/activate`
3. Ejecutar el siguiente comando con el entorno activado `pip install Flask flask-mysqldb flask-cors`

## Correr en local
Ejecutar `python app.py`