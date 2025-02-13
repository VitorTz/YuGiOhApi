from pydantic import BaseModel
from typing import Optional


class Card(BaseModel):

    name: str
    descr: str
    image_url: str
    attack: Optional[int] = None
    defence: Optional[int] = None
    level: Optional[int] = None    
    archetype: Optional[str] = None
    frame_type: Optional[str] = None
    race: Optional[str] = None
    card_type: Optional[str] = None
    attribute: Optional[str] = None
