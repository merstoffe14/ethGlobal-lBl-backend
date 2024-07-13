from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class Label(BaseModel):

    data_id: int
    label: str
    user_id: str

class Dataset(BaseModel):
    label_options: list
    owner_id: str
    name: str
    description: str