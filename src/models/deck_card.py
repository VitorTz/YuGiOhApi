from pydantic import BaseModel


class DeckCard(BaseModel):

    card_id: int
    deck_id: int
    num: int