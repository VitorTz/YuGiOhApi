from fastapi import APIRouter, Query, status
from fastapi.responses import Response, JSONResponse
from src.database import get_pool
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from src.models.character import Character
from src.query_constructor import QueryConstructor, Comparation, QueryComp
from typing import List


characters_router = APIRouter()


@characters_router.get("/characters", response_model=List[Character])
def get_character(
    character_id: int = Query(default=None),
    character_name: str = Query(default=None)
):
    q = QueryConstructor(table_prefix="c.")
    q.add(QueryComp('character_id', Comparation.EQUAL, character_id))
    q.add(QueryComp('name', Comparation.EQUAL, character_name))    
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
                        c.wiki_page_url                        
                    FROM 
                        characters c
                    {q.query()}
                """,
                q.values()
            )
            r = cur.fetchall()
            if r is None:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(r, status.HTTP_200_OK)


@characters_router.get("/characters/images", response_model=List[Character])
def get_character(character_id: int = Query()):    
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:            
            cur.execute(
                f"""
                    SELECT
                        i.image_url
                    FROM 
                        images i 
                    INNER JOIN
                        character_images ci
                    ON
                        ci.image_id = i.image_id
                    WHERE
                        ci.character_id = %s;
                """,
                (str(character_id), )
            )
            r = cur.fetchall()
            if r is None:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            images: list = []
            for image in r:
                images.append(image[0])
            return JSONResponse(images, status.HTTP_200_OK)


