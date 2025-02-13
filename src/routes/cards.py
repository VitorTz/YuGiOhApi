from fastapi import APIRouter, Query, status
from fastapi.responses import Response, JSONResponse
from src.database import get_pool
from src.models.card import Card
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from src.util.query_constructor import QueryConstructor
from typing import List


cards_router = APIRouter()


@cards_router.get("/cards", response_model=List[Card])
def read_card_query(
    card_id: int = Query(default=None),
    attribute: str = Query(default=None),
    frame_type: str = Query(default=None),
    archetype: str = Query(default=None),
    race: str = Query(default=None),
    card_name: str = Query(default=None),
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
    q.add_comp('attribute', '=', attribute)    
    q.add_comp('race', '=', race)
    q.add_search_term('name', card_name)
    q.add_comp('frame_type', '=', frame_type)
    q.add_comp('archetype', '=', archetype)
    q.add_comp('card_id', '=', card_id)
    q.add_comp_coalesce(
        [
            ('level', '=', level_equal),
            ('level', '>', level_greater),
            ('level', '>=', level_greater_or_equal),
            ('level', '<', level_less),
            ('level', '=<', level_less_or_equal)            
        ]
    )
    q.add_comp_coalesce(
        [
            ('attack', '=', attack_equal),
            ('attack', '>', attack_greater),
            ('attack', '<', attack_less),
            ('attack', '>=', attack_greater_or_equal),
            ('attack', '<=', attack_less_or_equal),
        ]
    )
    q.add_comp_coalesce(
        [
            ('defence', '=', defence_equal),
            ('defence', '>', defence_greater),
            ('defence', '<', defence_less),
            ('defence', '>=', defence_greater_or_equal),
            ('defence', '<=', defence_less_or_equal)
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
                        cards_images ci ON 
                        c.card_id = ci.card_id
                    {q.query()};
                """,
                q.values()
            )
            r = cur.fetchall()
            if not r:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(r, status.HTTP_200_OK)
