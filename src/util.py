from src.database import get_pool, db_open
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from pathlib import Path
from src.models.deck import Deck
import json


def load_json(path: Path):
    with open(path, "r") as file:
        return json.load(file)


def get_enum_list(enum_name: str) -> list[str]:
    enums: list[str] = []
    pool: ConnectionPool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT unnest(enum_range(NULL::{enum_name}));")
            r = cur.fetchall()
            enums: list[str] = []
            for i in r:
                enums.append(i[0])
    return enums

def get_deck_card_from_file(deck_file: Path) -> dict[int, int]:
    file = open(deck_file, "r")
    lines: list[str] = [x.strip() for x in file.readlines()]
    card_list: list[int] = [int(x) for x in lines if x.isalnum()]
    
    cards: dict[int, int] = {}
    for card in card_list:
        cards[card] = cards.get(card, 0) + 1
    
    return cards

def add_deck(deck: dict[str, str]) -> None:
    cards: dict[int, int] = get_deck_card_from_file(deck['file'])
    pool: ConnectionPool = get_pool()
    deck_id: int = None

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.row_factory = dict_row
            try:
                cur.execute(
                    """
                        INSERT INTO decks (
                            character_id,
                            franchise_id,
                            name,
                            descr
                        )
                        VALUES
                            (%s, %s, %s, %s)
                        ON CONFLICT                            
                        DO NOTHING
                        RETURNING
                            deck_id;
                    """,
                    (
                        str(deck['character_id']),
                        str(deck['franchise_id']),
                        deck['name'],
                        deck['descr']
                    )
                )
                r = cur.fetchone()
                conn.commit()
                if r is None:
                    print(f"deck {deck['name']} alread exists!")
                    return
                deck_id = r['deck_id']
            except Exception as e:
                print(e)
                print(f"EXCEPTION! could not create deck {deck['name']}")
                conn.rollback()
                return
            
    print(f"deck {deck['name']} created!")
    
    for card_id, num_cards in cards.items():
        with pool.connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                            INSERT INTO deck_cards (
                                card_id,
                                deck_id,
                                num_cards
                            )
                            VALUES
                                (%s, %s, %s)
                            ON CONFLICT
                            DO NOTHING
                        """,
                        (
                            str(card_id),
                            str(deck_id),
                            num_cards
                        )
                    )
                    conn.commit()
                    print(f"card {card_id} | {num_cards} add to deck {deck_id}")
                except Exception as e:
                    print(e)
                    print(f"colud not add card {card_id} to deck {deck_id}")
                    conn.rollback()
                    return


def register_decks() -> None:
    db_open()
    decks: list[dict[str, str]] = load_json("res/decks.json")
    for deck in decks:
        add_deck(deck)


def get_deck_by_deck_id(deck_id: int) -> Deck | None:
    pool: ConnectionPool = get_pool()

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute(
                """
                    SELECT
                        decks.deck_id,
                        decks.name AS deck_name,
                        characters.name AS character_name,
                        characters.character_id,
                        franchises.name AS franchise_name,
                        franchises.franchise_id,
                        decks.descr
                    FROM
                        decks
                    INNER JOIN
                        characters
                    ON
                        decks.character_id = characters.character_id
                    INNER JOIN
                        franchises
                    ON
                        decks.franchise_id = franchises.franchise_id
                    WHERE
                        decks.deck_id = %s
                """,
                (str(deck_id), )
            )
            deck = cur.fetchone()
            if deck is None:
                return None
            
            cur.execute(
                """
                    SELECT 
                        c.card_id,
                        c.name,
                        c.descr,
                        c.attack,
                        c.defence,
                        c.level,
                        c.race,
                        c.attribute,
                        c.card_type,
                        c.archetype,
                        c.frame_type,
                        dc.num_cards,
                        ci.image_url                            
                    FROM
                        deck_cards dc
                    INNER JOIN
                        cards c
                    ON
                        c.card_id = dc.card_id
                    INNER JOIN
                        card_images ci
                    ON
                        ci.card_id = dc.card_id                        
                    WHERE
                        dc.deck_id = %s;
                """,
                (str(deck_id), )
            )
            cards = cur.fetchall()
            deck['num_cards'] = 0
            for card in cards:
                deck['num_cards'] += card['num_cards']
            deck['cards'] = cards
            return deck
        

def register_deck_references() -> None:
    db_open()
    pool = get_pool()
    deck_ids: list[str] = []
    
    REFERENCES = [
        "attribute",
        "race",
        "card_type",
        "frame_type",
        "archetype"
    ]

    with pool.connection() as conn:
        with conn.cursor() as cur:            
            cur.execute(
                """
                    SELECT DISTINCT
                        deck_id
                    FROM
                        deck_cards;
                """
            )
            r = cur.fetchall()
            for i in r:
                deck_ids.append(i[0])
    
    for deck_id in deck_ids:
        deck: Deck = get_deck_by_deck_id(deck_id)
        for card in deck['cards']:
            for reference in REFERENCES:
                if card[reference] is None:
                    continue                
                with pool.connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                                SELECT 
                                    deck_reference_id
                                FROM
                                    deck_references
                                WHERE
                                    deck_id = %s AND
                                    {reference} = %s
                            """,
                            (str(deck_id), card[reference])
                        )
                        r = cur.fetchone()
                        if r is not None:
                            print(f"reference deck: {deck_id} {reference}: {card[reference]} already exists!")
                        if r is None:
                            cur.execute(
                                f"""
                                    INSERT INTO deck_references (
                                        deck_id,
                                        {reference}
                                    )
                                    VALUES
                                        (%s, %s)
                                """,
                                (str(deck_id), card[reference])
                            )
                            print(f"new reference deck: {deck_id} {reference}: {card[reference]}")                            
