# Sistema de gestión de proyectos con metodologías ágiles: KANBAN + SCRUM

## Proyecto de la materia Ingeniería de software II de la FP-UNA.

### Colaboradores

* José Luis Junior Gutiérrez Agüero [@jg2kpy](https://github.com/jg2kpy)
* Manuel René Pauls Toews [@QuisVenator](https://github.com/QuisVenator)
* Guillermo Pamplona Pardo [@guigapamplona](https://github.com/guigapamplona)

### Requisitos

* Docker
* Docker-compose

Clonar el repositorio con el siguente comando:

```bash
git clone https://github.com/jg2kpy/gestion_proyectos_agile.git
```

### Configuración

Antes de ejecutar los containers se debe realizar una copia de .env.example y renombrar a .env.desarrollo o .env.produccion y completar las variables de entorno

## Ejecutar

### Desarrollo

Ejecutar el docker compose con el archivo docker-compose.desarrollo.yaml, este comando sirve para generar las imágenes y ejecutar los containers automáticamente:

```bash
docker-compose -f "docker-compose.desarrollo.yaml" up --build
```

Desde otra instancia de una terminal se puede ejecutar las pruebas unitarias:

```bash
docker exec gpa-dev python3 manage.py test
```

Para generar la documentación automatica, que se puede acceder a ella mediante el puerto 8081:

```bash
docker exec gpa-dev ./docs/generar_doc_html.sh
```

Tambien se puede acceder al container de manera interactiva:

```bash
docker exec -it gpa-dev bash
```

Se debe ejecutar el script ./delete_migrations.sh si se pasa de trabajar de desarrollo a produccion

```bash
./delete_migrations.sh
```

### Produccion

Ejecutar el docker compose con el archivo docker-compose.desarrollo.yaml, este comando sirve para generar las imagenes y ejecutar los containers automaticamente:

```bash
docker-compose -f "docker-compose.produccion.yaml" up --build
```
