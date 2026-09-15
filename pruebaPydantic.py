
from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Union

app = FastAPI(title="Mini Blog")

BLOG_STATION = [
    {"id": 1, "station_name":"San Diego", "location":"California", "humidity":"90", "temperature":"24"},
    {"id": 2, "station_name":"Sandy", "location":"Utah", "humidity":"30", "temperature":"18"},
    {"id": 3, "station_name":"Raleighn", "location":"North Caroline", "humidity":"70", "temperature":"20"},
    
]

class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Nombre de la etiqueta")

class Fecha(BaseModel):
    name: str
    email: EmailStr

class Station(BaseModel):
    station_name: str 
    location:str
    humidity: float
    temperature: float
    tags: Optional[List[Tag]] = []
    fecha: Optional[Fecha] = None
    


class StationCreate(Station):
    station_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo de la estacion (mínimo 3 caracteres, máximo 100)",
        examples=["midvale"]
                  )
    location:str
    humidity: float
    temperature: float
    tags: Optional[List[Tag]] = []
    fecha: Optional[Fecha] = None

    @field_validator("station_name")
    @classmethod
    def not_allowed_title(cls, value:str) -> str:
        if "spam" in value.lower():
            raise ValueError("El título no puede contener la palabra: 'spam'")
        return value

class StationUpdate(BaseModel):
    station_name: str
    location:Optional[str]=None
    humidity: float
    temperature: float


#ejempllo de modelos que queremos regresar son plantillas 
class StationPublic(Station):
    id:int # agrego id porque en la clase Sation no esta este atributo

class StationSummary (BaseModel):
    id: int
    station_name: str   # tengo que heredar de BaseModel y no de Statiom porque solo quiero el atributo station name no los demas     
    humidity: float
    temperature: float

@app.get("/")
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get("/station", response_model=List[StationPublic])
def list_posts(query: str | None = Query(default=None, description="Texto para buscar por título")):
    
    if query:
        return [post for post in BLOG_STATION if query.lower() in  post["station_name"].lower() ]
        
    
    return BLOG_STATION
 
 
@app.get("/station/{post_id}", response_model=Union[StationPublic, StationSummary], response_description="Estacion encontrada")
def get_post(post_id: int, includelocation:bool = Query(default=True, description="Incluir o no la locacion")):
    for post in BLOG_STATION:
        if post["id"] == post_id:
            if not includelocation:
                return {"id": post["id"], "station_name": post["station_name"], "humidity":post["humidity"],"temperature": post["temperature"]}
            return post
    
    raise  HTTPException(status_code=404, detail="estacion no encontrado")

@app.post("/stations", response_model=StationPublic, response_description="Estacion creada")
def create_post(post: StationCreate ):
    new_id = (BLOG_STATION[-1]["id"]+1) if BLOG_STATION else 1
    new_post = {"id": new_id, "station_name": post.station_name, "location": post.location,
                "humidity":post.humidity, "temperature": post.temperature, 
                "tags": [tag.model_dump() for tag in post.tags],
                "fecha": post.fecha.model_dump() if post.fecha else None}
    BLOG_STATION.append(new_post)
    return new_post


@app.put("/stations/{post_id}", response_model=StationPublic, response_description="Estacion actualizada", response_model_exclude_none=True )
def update_post(post_id: int, data: StationUpdate):
    for post in BLOG_STATION:
        if post["id"] == post_id:
            playload= data.model_dump(exclude_unset=True)
            if "station_name" in playload: post["station_name"] = playload["station_name"]
            if "location" in playload: post["location"] = playload["location"]
            if "humidity" in playload: post["humidity"] = playload["humidity"]
            if "temperature" in playload: post["temperature"] = playload["temperature"]
            return post
    
    raise HTTPException(status_code=404, detail="estacion no encontrado")


@app.delete("/stations/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_STATION):
        if post["id"] == post_id:
            BLOG_STATION.pop(index)
            return
    raise HTTPException(status_code=404,detail="estacion no encontrado")