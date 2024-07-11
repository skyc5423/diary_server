from pydantic import BaseModel


class FastAPIMessage(BaseModel):
    content: str
