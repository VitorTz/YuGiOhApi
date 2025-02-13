import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from src.database import db_open, db_close, get_pool
import json
import os


load_dotenv()


STORAGE_ROOT_DIR = "yu-gi-oh"


def open_storage() -> None:
    cloudinary.config( 
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
        api_key = os.getenv('CLOUDINARY_CLOUD_API_KEY'), 
        api_secret = os.getenv('CLOUDINARY_CLOUD_API_SECRET'),
        secure=True
    )


def add_images() -> None:
    db_open()

    with open("not_found.txt", 'r') as file:
        not_found = [x.strip().lower() for x in file.readlines()]

    with open("res/cards_full_info.json", "r") as file:
        cards = json.load(file)

    pool: ConnectionPool = get_pool()
    for card_id in not_found:
        card: dict[str, str] = cards[card_id]
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.row_factory = dict_row
                try:
                    cur.execute(
                        """
                            INSERT INTO cards (
                                card_id,
                                name,
                                attack,
                                defence,
                                level,
                                archetype,
                                frame_type,
                                race,
                                card_type,
                                attribute,
                                descr
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
                                    %s,
                                )
                            ON CONFLICT
                                (card_id)
                            DO NOTHING;
                        """,
                        (
                            card_id,
                            card['name'],
                            card['atk'],
                            card['def'],
                            card['level'],
                            card['archetype'],
                            card['frameType'],
                            card['race'],
                            card['type'],
                            card['attribute'],
                            card['desc']
                        )                        
                    )
                    conn.commit()
                    print(f"card {card_id} uploaded!")
                except Exception as e:
                    print(e)
                    print(card_id)
                    conn.rollback()
                    db_close()
                    return
                

        # image_url = cards[card_id]['card_images'][0]['image_url']
        # result = cloudinary.uploader.upload(image_url, folder=f"{STORAGE_ROOT_DIR}/{card_id[0]}")
        #         try:
        #             if not result['secure_url']:
        #                 raise AttributeError()
                    
        #             cur.execute(
        #                 """
        #                     INSERT INTO cards_images (
        #                         card_id,
        #                         image_url
        #                     )
        #                     VALUES
        #                         (%s, %s)
        #                     ON CONFLICT
        #                         (card_id)
        #                     DO NOTHING;
        #                 """,
        #                 (card_id, result['secure_url'])
        #             )
        #             conn.commit()
        #         except Exception as e:
        #             print(e)
        #             conn.rollback()
        #             db_close()
        #             return
        #         print(f"card {card_id} uploaded!")        

    db_close()
    