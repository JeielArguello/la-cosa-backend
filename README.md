# Lanzallamas_Back_End

Repositorio backend para ingeniería del software 1.

# Instalación

## Creación entorno virtual

```
$ virtualenv venv
$ source ./venv/bin/activate
```

## Instalación packages

```
$ pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:home/<usuario>/<directorio_del_proyecto>/Back
```
## Correr el servidor

```
$ uvicorn main:app --reload
```

## Documentación

http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc

# Salir del entorno virtual

```
$ deactivate
```

# Correr test
```
$ export PYTHONPATH=$PYTHONPATH:home/<usuario>/<directorio_del_proyecto>/Back
$ pytest -vv
```