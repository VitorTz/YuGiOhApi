from pydantic import BaseModel


class Deck(BaseModel):

    deck_id: int
    name: str
    character_id: int
    desc: str