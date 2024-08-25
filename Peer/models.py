from pydantic import BaseModel

class File(BaseModel):
    name: str
    hash_value: int