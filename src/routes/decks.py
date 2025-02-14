from fastapi import APIRouter, Query, status
from fastapi.responses import Response, JSONResponse
from src.query_constructor import QueryConstructor, Comparation, QueryComp
from src.models.deck import Deck
from src.util import get_deck_by_deck_id
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from src.database import get_pool
from typing import List


decks_router = APIRouter()


@decks_router.get("/decks", response_model=List[Deck])
def get_deck(
    deck_id: int = Query(default=None),    
    attribute: str = Query(default=None)
):
    pool: ConnectionPool = get_pool()

    if deck_id:
        deck = get_deck_by_deck_id(deck_id)
        if deck is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return JSONResponse([deck])

    # 1. Query all decks ids
    q = QueryConstructor('drf.')
    q.add(QueryComp('attribute', Comparation.EQUAL, attribute))

    if q.is_empty:
        return Response()
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                    SELECT
                        d.deck_id
                    FROM
                        decks d                    
                    INNER JOIN
                        deck_references drf
                    ON
                        drf.deck_id = d.deck_id
                    {q.query()}                    
                """,
                q.values()
            )
            r = cur.fetchall()
            if not r:
                return Response(status.HTTP_404_NOT_FOUND)
            decks = []
            for result_list in r:
                decks.append(get_deck_by_deck_id(result_list[0]))
            return JSONResponse(decks)


@decks_router.get("/decks/random", response_model=Deck)
def get_random_deck():
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:            
            cur.execute(
                """
                    SELECT 
                        deck_id
                    FROM 
                        decks
                    ORDER BY 
                        random()
                    LIMIT 1;
                """
            )
            r = cur.fetchone()
            deck_id: int = r[0]
            deck = get_deck_by_deck_id(deck_id)
            return JSONResponse(deck)