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
$ export PYTHONPATH=~/<directorio_del_proyecto>/Back
$ pytest -vv
```

## Coverage por consola 

```
$ pytest --cov-report term-missing --cov=. tests/
```

## Coverage por html

```
$ pytest --cov-report html --cov=. tests/
```
