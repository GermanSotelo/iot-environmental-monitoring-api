from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class SensorReading(BaseModel):
    station_name: str
    temperature: float
    humidity: float

readings = []

@app.post("/readings")
def create_reading(reading: SensorReading):
    new_reading = {
        "id": len(readings) + 1,
        "station_name": reading.station_name,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "timestamp": datetime.now()
    }
    readings.append(new_reading)
    return new_reading

@app.get("/readings")
def get_readings():
    return readings

@app.get("/readings/{id}")
def get_reading(id: int):
    for r in readings:
        if r["id"] == id:
            return r
    return {"error": "Not found"}

@app.delete("/readings/{id}")
def delete_reading(id: int):
    for r in readings:
        if r["id"] == id:
            readings.remove(r)
            return {"message": "Deleted"}
    return {"error": "Not found"}