from psycopg_pool import ConnectionPool
from src.database import db_open, db_close, get_pool
from psycopg.rows import dict_row
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
import json
import os


load_dotenv()

def open_storage() -> None:
    cloudinary.config( 
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
        api_key = os.getenv('CLOUDINARY_CLOUD_API_KEY'), 
        api_secret = os.getenv('CLOUDINARY_CLOUD_API_SECRET'),
        secure=True
    )


def upload_image(image_url: str, folder: str) -> str:
    r = cloudinary.uploader.upload(image_url, folder=folder)
    return r['secure_url']



KEYS = [
    'name',
    'atk',
    'def',
    'level',
    'archetype',
    'frameType',
    'race',
    'type',
    'attribute',
    'desc'
]


def add_images() -> None:
    db_open()

    images: list[tuple[str, str]] = []

    pool: ConnectionPool = get_pool()    
    with pool.connection() as conn:
        with conn.cursor() as cur:                
            try:
                cur.execute(
                    """
                        SELECT
                            card_id, image_url
                        FROM
                            cards_images;                            
                    """
                )
                images = cur.fetchall()                
            except Exception as e:                    
                db_close()
                return


    for image in images:
        card_id, image_url = image
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
                            DO NOTHING;
                        """,
                        (card_id, image_url)
                    )
                    conn.commit()
                    print(f"card {card_id} with url {image_url} uploaded!")
                except Exception as e:
                    conn.rollback()                    
                    print(f"card {card_id} is not present in table cards")
                    with open("not_found.txt", "a") as file:                        
                        file.write(f"{card_id}\n")
        
            
    db_close()
    

def create_deck(
        character_id: int, 
        franchiese_id: int,
        deck_name: str,
        cards: list[str],
        deck_descr: str = None
    ) -> None:
    db_open()
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.row_factory = dict_row
            try:
                cur.execute(
                    """
                        INSERT INTO decks (
                            character_id,
                            name,
                            descr,
                            franchise_id
                        )
                        VALUES
                            (%s, %s, %s, %s)
                        RETURNING
                            deck_id
                    """,
                    (
                        str(character_id),
                        deck_name,
                        deck_descr,
                        str(franchiese_id)
                    )
                )
                deck_id = cur.fetchone()['deck_id']
                conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()
                db_close()
                return
    
    print(f"deck_id: {deck_id}")

    for card in cards:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        SELECT 
                            card_id
                        FROM 
                            cards
                        WHERE
                            card_id = %s;
                    """,
                    (str(card), )
                )
                r = cur.fetchone()
                if r is None:
                    print(f"card not found! {card}")
                    db_close()
                    return
                
                cur.execute(
                    """
                        INSERT INTO deck_cards (
                            card_id,
                            deck_id
                        )
                        VALUES
                            (%s, %s)
                        RETURNING
                            card_id;
                    """,
                    (str(card), str(deck_id))
                )
                r = cur.fetchone()
                conn.commit()
                if r is None:                    
                    print(card)
                    db_close()
                    return
                print(f"card {card} added to deck {deck_id}")
    
    db_close()