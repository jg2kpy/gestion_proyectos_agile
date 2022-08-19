source ./env_desarrollo.sh

pip install -r requirements.txt
pip install -r requirements-dev.txt

python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py runserver 0.0.0.0:8000
