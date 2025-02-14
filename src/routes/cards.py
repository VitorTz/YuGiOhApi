from fastapi import APIRouter, Query, status
from fastapi.responses import Response, JSONResponse
from src.database import get_pool
from src.models.card import Card
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from src.util import get_enum_list
from src.query_constructor import QueryConstructor, Comparation, QueryComp
from typing import List


cards_router = APIRouter()


@cards_router.get("/cards", response_model=List[Card])
def get_card(
    id: int = Query(default=None),
    attribute: str = Query(default=None),
    frame_type: str = Query(default=None),
    archetype: str = Query(default=None),
    race: str = Query(default=None),
    name: str = Query(default=None),
    level_equal: int = Query(default=None),
    level_greater: int = Query(default=None),
    level_greater_or_equal: int = Query(default=None),
    level_less: int = Query(default=None),
    level_less_or_equal: int = Query(default=None),
    attack_equal: int = Query(default=None),
    attack_greater: int = Query(default=None),
    attack_less: int = Query(default=None),
    attack_greater_or_equal: int = Query(default=None),
    attack_less_or_equal: int = Query(default=None),
    defence_equal: int = Query(default=None),
    defence_greater: int = Query(default=None),
    defence_greater_or_equal: int = Query(default=None),
    defence_less: int = Query(default=None),
    defence_less_or_equal: int = Query(default=None)
):    
    q = QueryConstructor(table_prefix="c.")
    if attribute: attribute = attribute.upper()
    q.add(QueryComp('attribute', Comparation.EQUAL, attribute))
    q.add(QueryComp('race', Comparation.EQUAL, race))    
    q.add(QueryComp('name', Comparation.SEARCH_TERM, name))
    q.add(QueryComp('frame_type', Comparation.EQUAL, frame_type))
    q.add(QueryComp('archetype', Comparation.EQUAL, archetype))
    q.add(QueryComp('card_id', Comparation.EQUAL, id))
    q.add_coalesce(
        [
            QueryComp('level', Comparation.EQUAL, level_equal),
            QueryComp('level', Comparation.GREATER, level_greater),
            QueryComp('level', Comparation.GREATER_OR_EQUAL, level_greater_or_equal),
            QueryComp('level', Comparation.LESS, level_less),
            QueryComp('level', Comparation.LESS_OR_EQUAL, level_less_or_equal)            
        ]
    )
    q.add_coalesce(
        [
            QueryComp('attack', Comparation.EQUAL, attack_equal),
            QueryComp('attack', Comparation.GREATER, attack_greater),
            QueryComp('attack', Comparation.GREATER_OR_EQUAL, attack_greater_or_equal),
            QueryComp('attack', Comparation.LESS, attack_less),
            QueryComp('attack', Comparation.LESS_OR_EQUAL, attack_less_or_equal)            
        ]
    )
    q.add_coalesce(
        [
            QueryComp('defence', Comparation.EQUAL, defence_equal),
            QueryComp('defence', Comparation.GREATER, defence_greater),
            QueryComp('defence', Comparation.GREATER_OR_EQUAL, defence_greater_or_equal),
            QueryComp('defence', Comparation.LESS, defence_less),
            QueryComp('defence', Comparation.LESS_OR_EQUAL, defence_less_or_equal)            
        ]
    )
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute(
                f"""
                    SELECT DISTINCT
                        c.card_id,
                        c.name,
                        c.descr,
                        c.attack,
                        c.defence,
                        c.level,
                        c.archetype,
                        c.card_type,
                        c.frame_type,
                        c.race,
                        c.attribute,
                        ci.image_url
                    FROM 
                        cards c
                    LEFT JOIN 
                        card_images ci ON 
                        c.card_id = ci.card_id
                    {q.query()};
                """,
                q.values()
            )
            r = cur.fetchall()
            if not r:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(r, status.HTTP_200_OK)


@cards_router.get("/cards/attributes", response_model=List[str])
def get_all_card_attributes():
    return JSONResponse(get_enum_list("attribute"))

    
@cards_router.get("/cards/races", response_model=List[str])
def get_all_card_races():
    return JSONResponse(get_enum_list("race"))


@cards_router.get("/cards/archetypes", response_model=List[str])
def get_all_card_archetypes():
    return JSONResponse(get_enum_list("archetype"))

@cards_router.get("/cards/card_types", response_model=List[str])
def get_all_card_types():
    return JSONResponse(get_enum_list("card_type"))


@cards_router.get("/cards/frame_types", response_model=List[str])
def get_all_card_frame_types():
    return JSONResponse(get_enum_list("frametype"))