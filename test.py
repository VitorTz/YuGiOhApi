from src.util import register_decks, register_deck_references
from src.database import db_open, db_close



def main() -> None:    
    db_open()
    register_deck_references()
    db_close()


if __name__ == "__main__":
    main()