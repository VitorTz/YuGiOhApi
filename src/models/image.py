from pydantic import BaseModel


class Image(BaseModel):
    
    image_url: str
    descr: str


class CardImage(BaseModel):

    card_id: int
    image_url: str