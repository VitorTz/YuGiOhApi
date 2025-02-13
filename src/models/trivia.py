from pydantic import BaseModel


class Trivia(BaseModel):

    trivia_id: int
    descr: str

    