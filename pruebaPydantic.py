
from fastapi import FastAPI, Query, Body, HTTPException, Path
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Literal, Optional, Union
from math import ceil

app = FastAPI(title="Mini Blog")

BLOG_STATION = [
    {"id": 1, "station_name":"San Diego", "location":"California", "humidity":"90", "temperature":"24"},
    {"id": 2, "station_name":"Sandy", "location":"Utah", "humidity":"30", "temperature":"18"},
    {"id": 3, "station_name":"Raleighn", "location":"North Caroline", "humidity":"70", "temperature":"20"},
    {"id": 4, "station_name":"Bogota", "location":"California", "humidity":"90", "temperature":"24"},
    {"id": 5, "station_name":"Medellin", "location":"Utah", "humidity":"30", "temperature":"18"},
    {"id": 6, "station_name":"Cali", "location":"North Caroline", "humidity":"70", "temperature":"20"},
    {"id": 7, "station_name":"Madrid", "location":"California", "humidity":"90", "temperature":"24"},
    {"id": 8, "station_name":"Barcelona", "location":"Utah", "humidity":"30", "temperature":"18"},
    {"id": 9, "station_name":"Berlin", "location":"North Caroline", "humidity":"70", "temperature":"20"},
    {"id": 10, "station_name":"Paris", "location":"California", "humidity":"90", "temperature":"24"},
    {"id": 11, "station_name":"Rona", "location":"Utah", "humidity":"30", "temperature":"18"},
    {"id": 12, "station_name":"Lisboa", "location":"North Caroline", "humidity":"70", "temperature":"20"},
     {"id": 13, "station_name":"Paris", "location":"California", "humidity":"90", "temperature":"24"},
    {"id": 14, "station_name":"Rona", "location":"Utah", "humidity":"30", "temperature":"18"},
    {"id": 15, "station_name":"Lisboa", "location":"North Caroline", "humidity":"70", "temperature":"20"},
    
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
    tags: Optional[List[Tag]] = Field (default_factory=list)
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
    tags: Optional[List[Tag]] = Field (default_factory=list)
    fecha: Optional[Fecha] = None

    @field_validator("station_name")
    @classmethod
    def not_allowed_title(cls, value:str) -> str:
        if "spam" in value.lower():
            raise ValueError("El título no puede contener la palabra: 'spam'")
        return value

class StationUpdate(BaseModel):
    station_name: Optional[str]=Field(None, min_length=3, max_length=100)
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

class PaginatedPost(BaseModel): #esta clase la usamos para usar paginacion una forma util de evitar que devolavamos demasiada informacion innecesaria y poner el servidor demasiado lento
    
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[StationPublic]  

@app.get("/")
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get("/station", response_model=PaginatedPost)
def list_posts(
    query: Optional[str]= Query(
        default=None,
        description="Texto para buscar por título",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"#es para indicar que tipo de caracteres acepta
    ),

    per_page: int = Query(
        10, ge=1, le=50,
        description="Número de resultados (1-50)"
    ),
    page: int = Query(
        1, ge=1,#minimo de la pagina que obvio debe empezar en 1
        description="Número de página (>=1)"
    ),
    order_by: Literal["id", "title"] = Query(
        "id", description="Campo de orden"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Dirección de orden"
    ) 


):
    
    results = BLOG_STATION


    if query:
        results = [post for post in results if query.lower()
                   in post["title"].lower()]

    total = len(results)
    total_pages = ceil(total/per_page) if total > 0 else 0#total de paginas con redondeo

    if total_pages == 0:
        current_page = 1
    else:
        current_page = min(page, total_pages) #escoge el menor de estos dos valores

    results = sorted(
        results, key=lambda post: post[order_by], reverse=(direction == "desc"))

    if total_pages == 0:
        items = []
    else:
        start = (current_page - 1) * per_page
        items = results[start: start + per_page]  # [10:20]

    has_prev = current_page > 1 #para indicarnos si hay o no paginas anteriores tna solo retrona true or false
    has_next = current_page < total_pages if total_pages > 0 else False #para indicarnos si hay o no paginas posteriores tna solo retrona true or false

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )
        
    
 
 
@app.get("/station/{post_id}", response_model=Union[StationPublic, StationSummary], response_description="Estacion encontrada")
def get_post(post_id: int=Path(
    ...,
    get=1,
    title="Id del post",
    description="debe ser mayor a 0",
    example=1
), includelocation:bool = Query(default=True, description="Incluir o no la locacion")):
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