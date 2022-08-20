# Sistema de gestión de proyectos con metodologías ágiles: KANBAN + SCRUM
## Proyecto de la materia Ingeniería de software II de la FP-UNA.

### Colaboradores
* José Luis Junior Gutiérrez Agüero [@jg2kpy](https://github.com/jg2kpy)
* Manuel René Pauls Toews [@QuisVenator](https://github.com/QuisVenator)
* Guillermo Pamplona Pardo [@guigapamplona](https://github.com/guigapamplona)
* Francisco Alejandro Sanabria Zelaya [@frandepy2](https://github.com/frandepy2)

### Requisitos
* Docker

Clonar el repositorio con el siguente comando:
```bash
git clone https://github.com/jg2kpy/gestion_proyectos_agile.git
```

## Ejecutar
### Desarrollo
Crear la imagen de desarrollo (solo primera ejecución):
```bash
docker build -t gpa-desarrollo -f Dockerfile.desarrollo .
```

Correr el servidor en docker (desde el directorio de este archivo):
```bash
docker run -p 80:8000 -v "$(pwd)":/home/ubuntu/app -it gpa-desarrollo
```

En caso de cambios al archivo `Dockerfile.desarrollo` elimar la imágen con:
```bash
docker image -rm gpa-desarrollo
```
y volver a crear la imagen.

### Producción
Crear la imagen de producción (solo primera ejecución):
```bash
docker build -t gpa-produccion -f Dockerfile.produccion .
```

Completar el archivo `produccion.sh.example`, cambiar el nombre del archivo a `produccion.sh` 
y correr el servidor en docker (desde el directorio de este archivo):
```bash
docker run -p 80:8000 -v "$(pwd)":/home/ubuntu/app -it gpa-produccion
```

En caso de cambios al archivo `Dockerfile.produccion` elimar la imágen con:
```bash
docker image -rm gpa-produccion
```
y volver a crear la imagen.