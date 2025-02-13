from fastapi import APIRouter, Query, status
from fastapi.responses import Response, JSONResponse
from src.database import get_pool
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from src.models.image import CardImage
from src.models.character import Character
from src.util.query_constructor import QueryConstructor
from typing import List


characters_router = APIRouter()


@characters_router.get("/characters", response_model=List[Character])
def read_character(
    character_id: int = Query(default=None),
    character_name: str = Query(default=None)
):
    q = QueryConstructor(table_prefix="c.")
    q.add_comp("character_id", '=', character_id)
    q.add_comp("name", '=', character_name)
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute(
                f"""
                    SELECT DISTINCT
                        c.character_id,
                        c.name,
                        c.bio,
                        c.wiki_page_url,
                        c.height::double precision,
                        c.weight::double precision,
                        pi.image_url AS perfil_image_url,
                        i.image_url AS image_url,
                        c.personality
                    FROM 
                        public.characters c
                    INNER JOIN 
                        public.images pi ON c.perfil_image_id = pi.image_id
                    INNER JOIN 
                        public.images i ON c.image_id = i.image_id
                    {q.query()}
                """,
                q.values()
            )
            r = cur.fetchall()
            if r is None:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(r, status.HTTP_200_OK)


