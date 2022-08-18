if [ -f ./env_produccion.sh ]; then
    source ./env_produccion.sh
    
    pip install -r requirements.txt
    pip uninstall -r requirements-dev.txt

    python manage.py makemigrations
    python manage.py migrate

    python manage.py runserver
else
    echo "Archivo con variables de entorno para produccion no existe"
fi  