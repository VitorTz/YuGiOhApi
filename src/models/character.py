from pydantic import BaseModel


class Character(BaseModel):


    name: str
    bio: str
    perfil_image_url: str
    image_url: str
    wiki_page_url: str
    height: float
    weight: float
    personality: str