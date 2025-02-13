from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse, Response
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from src.database import get_pool
from src.models.item import Item
from src.util.query_constructor import QueryConstructor
from typing import List

items_router = APIRouter()


@items_router.get("/items", response_model=List[Item])
def read_item(
    item_id: int = Query(default=None),
    item_type: str = Query(default=None),
    item_name: str = Query(default=None),
    character_id: int = Query(default=None, description="search for items related to character")
):
    q = QueryConstructor(table_prefix='i.')
    q.add_comp('item_id', '=', item_id)
    q.add_comp('item_type', '=', item_type)
    q.add_comp('character_id', '=', character_id, table_prefix='ir.')
    q.add_search_term('name', item_name)
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute(
                f"""
                    SELECT DISTINCT
                        i.item_id,
                        i.item_type,
                        i.image_id,
                        i.descr,                        
                        i.name,
                        imgs.image_url,
                        i.wiki_page_url
                    FROM 
                        items i
                    INNER JOIN 
                        items_relations ir ON 
                        i.item_id = ir.item_id
                    INNER JOIN
                        images imgs ON
                        i.image_id = imgs.image_id
                    {q.query()}
                """,
                q.values()
            )
            r = cur.fetchall()
            if not r:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            return JSONResponse(r, status_code=status.HTTP_200_OK)
            