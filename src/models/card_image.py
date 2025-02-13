from pydantic import BaseModel


class CardImage(BaseModel):

    card_id: int
    image_url: int