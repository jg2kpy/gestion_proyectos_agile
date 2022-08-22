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

### Configuración
Antes de ejecutar los containers se debe realizar una copia de .env.example y renombrar a .env.desarrollo o .env.produccion y completar las variables de entorno

## Ejecutar
### Desarrollo
Ejecutar el docker compose con el archivo docker-compose.desarrollo.yaml, este comando sirve para generar las imágenes y ejecutar los containers automáticamente:
```bash
docker-compose -f "docker-compose.desarrollo.yaml" up --build
```

Desde otra instancia de una terminal se puede acceder al container de la aplicacion con este comando:
```bash
docker exec -it gpa-dev bash
```

Desde esta consola se pueden ejecutar también todas las pruebas unitarias:
```bash
python3 manage.py test pruebas_unitarias.models.[TESTSUITE]
```

O generar la documentación automatica, que se puede acceder a ella mediante el puerto 8081:
```bash
chmod +x ./docs/generar_doc_html.sh
./docs/generar_doc_html.sh
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
