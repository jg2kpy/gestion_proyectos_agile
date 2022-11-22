#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi
printf "\nScript de ejecución automatica\n\n"
echo "El script necesita de permisos de super usuario para poder realizar limpiza de BD y migraciones"
sudo rm -rf ./postgre-data
sudo rm -rf ./*/migrations

declare -A iteraciones
iteraciones["v0.1-entorno"]="v0.1-entorno"
iteraciones["Iteracion_1"]="Iteracion_1"
iteraciones["Iteracion-1"]="Iteracion_1"
iteraciones["Iteracion-2"]="Iteracion-2"
iteraciones["Iteracion-3"]="Iteracion-3"
iteraciones["Iteracion-4"]="Iteracion-4"
iteraciones["Iteracion-5"]="Iteracion-5"

# tag=""

# if [ $# -eq 1 ];then
#     if [ -v iteraciones[$1] ]; then
#         tag=$1
#     else
#         echo "Este tag no existe, por favor seleccione uno correcto"
#     fi
# elif [ $# -gt 1 ];then
#     echo "USO:"
#     echo "  ./run.sh [arguments]"
#     echo "Comandos habilitados:"
#     echo "  help"
#     echo "  Iteracion-1"
#     echo "  Iteracion-2"
#     echo "  Iteracion-3"
#     echo "  Iteracion-4"
#     echo "  Iteracion-5"
#     exit
# fi

# if [ -z "$tag" ];then
#     printf "\nSeleccione un tag\n"
#     echo "1) Iteracion-1"
#     echo "2) Iteracion-2"
#     echo "3) Iteracion-3"
#     echo "4) Iteracion-4"
#     echo "5) Iteracion-5"
#     echo "Ctrl-C para salir"
#     read opcion
#     if [[ $opcion -ge 6 || $opcion -le 0 ]]; then
#         echo "Opcion no valida"
#         exit
#     fi
#     tag="Iteracion-${opcion}"
#     if [ $opcion -eq 1 ];then
#         tag="Iteracion_1"
#     fi
# fi

# if [ ! -v iteraciones[$tag] ]; then
#     echo "Iteracion no valida"
#     exit
# fi

# echo "El tag seleccionado es ${tag}"
# git checkout $tag

printf "\nEn que entorno le gustaria ejecutar?\n"
echo "1) Producción"
echo "2) Desarrollo"

read entorno

if [ $entorno -eq 1 ];then
    printf "\nEjecutando en entorno de producción...\n"
    $docker -f "docker-compose.produccion.yaml" up --build -d
    sleep 4
    if [ $tag = "Iteracion-5" ];then
        printf "\nLe gustaria cargar los datos de prueba?[s/n]\n"
        read opcion
        if [ $opcion = "s" ];then
            echo "Cargando datos de prueba..."
            docker exec gpa-pro python3 manage.py loaddata databasedump_prueba.json
        fi
    fi
    while [ true ]
    do
    printf "\nLe gustaria terminar con la ejecución en el entorno de producción?[s/n]\n"
    read opcion
    if [ $opcion = "s" ];then
        printf "\nTerminando la ejecución en entorno de producción...\n\n"
        $docker -f "docker-compose.produccion.yaml" stop
        exit
    fi
    done
else
    printf "\nEjecutando en entorno de desarrollo...\n"
    $docker -f "docker-compose.desarrollo.yaml" up --build -d
    sleep 4
    if [ $tag = "Iteracion-5" ];then
        printf "\nLe gustaria cargar los datos de prueba?[s/n]\n"
        read opcion
        if [ $opcion = "s" ];then
            echo "Cargando datos de prueba..."
            docker exec gpa-dev python3 manage.py loaddata databasedump_prueba.json
        fi
    fi
    while [ true ]
    do
        printf "\n\nMenu de desarrollo\n"
        echo "1) Ejecutar las pruebas unitarias"
        echo "2) Generar la documentación automatica"
        echo "3) Terminar la ejecución"
        read opcion
        if [ $opcion -eq 1 ];then
            printf "\nEjecutando las pruebas unitarias...\n"
            docker exec gpa-dev python3 manage.py test
        elif [ $opcion -eq 2 ];then
            printf "\nEjecutando las documentación autogenerada... (accesible desde http://localhost:8081/, Ctrl+C para terminar)\n\n"
            docker exec gpa-dev ./docs/generar_doc_html.sh
        else
            printf "\nTerminando la ejecución en entorno de desarrollo...\n\n"
            $docker -f "docker-compose.desarrollo.yaml" stop
            exit
        fi
    done
fi
