from pydantic import BaseModel

class CategoriaBase(BaseModel):
    nombre: str
    color: str = "#d1d4dc"

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True
