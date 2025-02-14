from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os


load_dotenv()


pool = ConnectionPool(
    conninfo=f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')} host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')}",
    min_size=4,
    max_size=10,
    timeout=30,
    open=False,
    max_waiting=4
)

is_pool_open = False


def db_open() -> None:
    global pool, is_pool_open
    if is_pool_open is False:
        pool.open()
        is_pool_open = True


def db_close() -> None:
    global pool
    pool.close()


def get_pool() -> ConnectionPool:
    global pool
    return pool
