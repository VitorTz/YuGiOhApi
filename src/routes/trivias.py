from fastapi import APIRouter, Query, status
from fastapi.responses import Response, JSONResponse
from src.database import get_pool
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from src.util.query_constructor import QueryConstructor
from src.models.trivia import Trivia
from typing import List


trivias_router = APIRouter()


@trivias_router.get("/trivias", response_model=List[Trivia])
def read_trivia(
    trivia_id: int = Query(default=None),
    search_term: str = Query(default=None),
    character_id: int = Query(default=None, description="Search for a trivia related to the character")
):
    q = QueryConstructor('t.')
    q.add_comp('trivia_id', '=', trivia_id)
    q.add_search_term('descr', search_term)
    q.add_comp('character_id', '=', character_id, 'ctm.')
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
       with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute(
            f"""
                SELECT DISTINCT
                    t.trivia_id,
                    t.descr                    
                FROM 
                    trivias t
                INNER JOIN 
                    character_trivia_mentions ctm ON 
                    t.trivia_id = ctm.trivia_id
                {q.query()}   
            """,
            q.values()
            )
            r = cur.fetchall()
            if not r:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(r, status_code=status.HTTP_200_OK)
       

@trivias_router.get("/trivias/random", response_model=Trivia)
def read_random_trivia():
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
       with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute(
                """
                    SELECT 
                        trivia_id,
                        descr                        
                    FROM 
                        trivias
                    ORDER BY 
                        random()
                    LIMIT 1;
                """
            )
            r = cur.fetchone()
            return JSONResponse(r, status.HTTP_200_OK)
