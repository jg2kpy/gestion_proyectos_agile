# Sistema de gestión de proyectos con metodologías ágiles: KANBAN + SCRUM
## Proyecto de la materia Ingeniería de software II de la FP-UNA.

### Colaboradores
* José Luis Junior Gutiérrez Agüero [@jg2kpy](https://github.com/jg2kpy)
* Manuel René Pauls Toews [@QuisVenator](https://github.com/QuisVenator)
* Guillermo Pamplona Pardo [@guigapamplona](https://github.com/guigapamplona)
* Francisco Alejandro Sanabria Zelaya [@frandepy2](https://github.com/frandepy2)

### Requisitos
* Docker
* Docker-compose

Clonar el repositorio con el siguente comando:
```bash
git clone https://github.com/jg2kpy/gestion_proyectos_agile.git
```

## Ejecutar
### Desarrollo
Ejecutar el docker compose con el archivo docker-compose.desarrollo.yaml, este comando sirve para generar las imagenes y ejecutar los containers automaticamente:
```bash
docker-compose -f "docker-compose.desarrollo.yaml" up --build
```

### Produccion
Ejecutar el docker compose con el archivo docker-compose.desarrollo.yaml, este comando sirve para generar las imagenes y ejecutar los containers automaticamente:
```bash
docker-compose -f "docker-compose.produccion.yaml" up --build
```

Para generar los archivos estaticos para NGINX se debe ejecutar
```bash
docker exec -it gpa-pro python3 manage.py collectstatic
```