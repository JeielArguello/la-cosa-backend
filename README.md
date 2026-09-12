# Lanzallamas Backend

Backend del juego **La Cosa**, desarrollado con FastAPI para Ingeniería del
Software 1. La aplicación gestiona usuarios, partidas, cartas y comunicación
en tiempo real mediante WebSockets.

## Tecnologías

- Python
- FastAPI y Uvicorn
- Pony ORM
- SQLite
- Pytest y pytest-cov

## Requisitos

- Python 3.9 o superior
- `pip`

## Instalación

Desde la raíz del proyecto, crea y activa un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecutar la API

Inicia el servidor de desarrollo con:

```bash
uvicorn main:app --reload
```

La API quedará disponible en <http://127.0.0.1:8000>. Al iniciar la
aplicación se crea la base de datos SQLite y se cargan las cartas iniciales.

## Documentación de la API

FastAPI genera documentación interactiva automáticamente:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

Los principales grupos de endpoints son:

| Prefijo | Responsabilidad |
| --- | --- |
| `/user` | Usuarios |
| `/match` | Salas y partidas |
| `/game` | Lógica de juego |
| `/ws` | Comunicación en tiempo real por WebSockets |

La ruta `GET /` sirve como comprobación rápida de que la API está activa.

## Estructura del proyecto

```text
├── endpoints/   # Rutas HTTP y WebSockets
├── logic/       # Reglas y efectos del juego
├── models/      # Modelos, persistencia y cartas
├── utils/       # Funciones auxiliares
├── tests/       # Tests de endpoints, lógica, modelos y utilidades
├── main.py      # Configuración y punto de entrada de FastAPI
└── requirements.txt
```

## Ejecutar los tests

Con el entorno virtual activo, ejecuta toda la suite:

```bash
PYTHONPATH=. pytest -vv
```

Para obtener cobertura en la terminal:

```bash
PYTHONPATH=. pytest --cov=. --cov-report=term-missing
```

Para generar un informe HTML:

```bash
PYTHONPATH=. pytest --cov=. --cov-report=html
```

El informe se genera en `htmlcov/index.html`.

## Finalizar el entorno virtual

```bash
deactivate
```
