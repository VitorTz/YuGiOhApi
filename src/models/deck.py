from pydantic import BaseModel
from src.models.card import Card


class Deck(BaseModel):

    deck_id: int
    deck_name: str
    character_name: str
    character_id: int
    franchise_name: str
    franchise_id: int
    descr: str
    cards: list[Card]
    num_cards: int