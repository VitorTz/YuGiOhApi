import json
from psycopg_pool import ConnectionPool
from src.storage import open_storage, upload_image
from src.database import db_open, db_close, get_pool


def load_json(path: str):
    with open(path, "r") as file:
        return json.load(file)
    

cards: dict[str, dict[str, str]] = load_json("res/cards_full_info.json")


KEYS = [    
    'name',
    'desc',
    'archetype',
    'attribute',
    'atk',
    'def',
    'frameType',
    'race',
    'level',
    'type'
]


def card_exists(card_id: int) -> bool:
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT card_id FROM cards WHERE card_id = %s;",
                (str(card_id), )
            )
            r = cur.fetchone()
            if r is None:
                return False
            return True
        
def create_card(card: dict[str, str]) -> bool:
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                        INSERT INTO cards (
                            card_id,
                            name,
                            descr,
                            archetype,
                            attribute,
                            attack,
                            defence,
                            frame_type,
                            race,
                            level,
                            card_type
                        )
                        VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s
                            )
                        ON CONFLICT
                            (card_id)
                        DO NOTHING
                        RETURNING
                            card_id;
                    """,
                    (
                        str(card['id']),
                        card['name'],
                        card['desc'],
                        card['archetype'],
                        card['attribute'],
                        card['atk'],
                        card['def'],
                        card['frameType'],
                        card['race'],
                        card['level'],
                        card['type']
                    )
                )
                r = cur.fetchone()
                conn.commit()
                if r is not None:
                    print(f"card {card['name']} | {card['id']} created!")
                    return True
            except Exception as e:
                print(e)
                print(f"EXPCETION -> {card}")
                conn.rollback()                
    return False

def create_card_image(card_id: int, image_url: str) -> bool:
    secure_url: str = upload_image(image_url, f"yu-gi-oh/{str(card_id)[0]}")
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                        INSERT INTO card_images (
                            card_id,
                            image_url
                        )
                        VALUES  
                            (%s, %s)
                        ON CONFLICT
                            (card_id)
                        DO NOTHING
                        RETURNING
                            card_id;
                    """,
                    (str(card_id), secure_url)
                )
                r = cur.fetchone()
                if r is not None:
                    print(f"image for card {card_id} created!")
                    return True
                conn.commit()
            except Exception as e:
                print(e)
                print(f"EXCEPTION -> {card_id}")
                conn.rollback()
    return False

def main() -> None:
    db_open()
    open_storage()
    n = 0
    for card in cards.values():        
        n += 1
        card_info = {k: card.get(k) for k in KEYS}
        try:
            images: list[dict[str, str]] = card['card_images']
            for image in images:                
                card_info['id'] = image['id']
                card_id = image['id']
                image_url = image['image_url']
                if card_id != card['id']:                    
                    create_card(card_info)                    
                    create_card_image(card_id, image_url)
        except Exception as e:
            print(e)
            print(card)
            db_close()
            return

    db_close()
    

if __name__ == "__main__":
    main()