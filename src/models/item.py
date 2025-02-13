from pydantic import BaseModel


class Item(BaseModel):

    item_id: int
    name: str
    item_type: str
    image_url: str
    wiki_page_url: str
    descr: str