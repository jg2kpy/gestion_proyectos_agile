#!/bin/sh

### Ejecutar desde la raiz del proyecto ###

# Entrar en el directorio docs
cd docs

# Borrar Carpeta _build
rm -rf _build

# Borrar todos los rst excepto index
mv index.rst index.rst.temp
rm *.rst
mv index.rst.temp index.rst

# ejecutar el api-doc
sphinx-apidoc -o . ..
make html

sphinx-serve
