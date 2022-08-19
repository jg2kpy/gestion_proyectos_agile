# Sistema de gestión de proyectos con metodologías ágiles: KANBAN + SCRUM
## Proyecto de la materia Ingeniería de software II de la FP-UNA.

### Colaboradores:
* José Luis Junior Gutiérrez Agüero [@jg2kpy](https://github.com/jg2kpy)
* Manuel René Pauls Toews [@QuisVenator](https://github.com/QuisVenator)
* Guillermo Pamplona Pardo [@guigapamplona](https://github.com/guigapamplona)
* Francisco Alejandro Sanabria Zelaya [@frandepy2](https://github.com/frandepy2)

### Requisitos:
* Python 3.10
* Django 4.1

Clonar el repositorio con el siguente comando:

```
$ git clone https://github.com/jg2kpy/gestion_proyectos_agile.git
```

Volvemos ejecutable el script para instalar las primeras dependencias:
```
$ chmod +x first_start.sh
```

Ejecutamos el script que instala las primeras dependencias:
```
# ./first_start.sh
```

Una vez termina ejecutamos el entorno virtual:
```
$ source ./venv/bin/activate
```

Despues iniciamos la base de datos de desarrollo:
```
# ./init_db_desarrollo.sh
```

Finalmente instalamos las ultimas dependencias, hacemos migraciones y ejecutamos el software:
```
$ ./run_desarrollo.sh
```

### Docker:
En caso de querer ejecutar con un Docker debemos clonar el repositorio y construir la imagen:
```
$ docker build -t is2 .
```

Luego ejecutamos la imagen y seguimos los pasos desde la ejecucion del entorno virtual
```
$ docker run -it is2:latest
```
