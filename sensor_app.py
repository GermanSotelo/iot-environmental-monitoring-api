from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, SensorReading

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/readings")
def create_reading(station_name: str, temperature: float, humidity: float, db: Session = Depends(get_db)):
    reading = SensorReading(station_name=station_name, temperature=temperature, humidity=humidity)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

@app.get("/readings")
def get_readings(db: Session = Depends(get_db)):
    return db.query(SensorReading).all()#es equivalentea SELECT * FROM readings

@app.get("/readings/{id}")
def get_reading(id: int, db: Session = Depends(get_db)):
    return db.query(SensorReading).filter(SensorReading.id == id).first()#es equivalentea SELECT * FROM readings WHERE id = 1

@app.put("/readings/{id}")
def update_reading(id: int, station_name: str, temperature: float, humidity: float, db: Session = Depends(get_db)):
    reading = db.query(SensorReading).filter(SensorReading.id == id).first()
    if reading:
        reading.station_name = station_name
        reading.temperature = temperature
        reading.humidity = humidity
        db.commit()
        db.refresh(reading)
        return reading
    return {"error": "Not found"}



@app.delete("/readings/{id}")
def delete_reading(id: int,  db: Session = Depends(get_db)):
    reading = db.query(SensorReading).filter(SensorReading.id == id).first()
    if reading:
        db.delete(reading)
        db.commit()
        return {"message": "Deleted"}
    return {"error": "Not found"}   