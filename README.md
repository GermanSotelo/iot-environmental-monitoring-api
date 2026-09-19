# IoT Environmental Monitoring API

REST API for environmental station monitoring built with FastAPI.

## Features
- CRUD operations for environmental stations
- Pydantic validation
- Query filtering and pagination
- Error handling with HTTP exceptions

## Tech Stack
- Python 3.13
- FastAPI
- Pydantic
- SQLite (moving to PostgreSQL)

## Installation
```bash
git clone https://github.com/tuusuario/iot-environmental-monitoring-api
cd iot-environmental-monitoring-api
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```

## Run
```bash
fastapi dev main.py
```

API docs available at: http://127.0.0.1:8000/docs
