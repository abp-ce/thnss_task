import os
import sqlite3
from urllib.parse import urlparse

import pandas as pd

from technesis.constants import (
    DB_NAME,
    SAVE_PATH,
)


def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def prepare_data(df: pd.DataFrame, sender_id: int) -> pd.DataFrame:
    df["price"] = None
    df["sender_id"] = sender_id
    return df


def remove_sender_data_from_db(conn, sender_id: int) -> None:
    from technesis.config import logger

    try:
        cursor = conn.cursor()
        query = "DELETE FROM prices WHERE sender_id = ?"
        cursor.execute(query, (sender_id,))
        logger.info(f"Deleted data from DB for sender_id: {sender_id}")
    except sqlite3.Error as e:
        logger.error(f"Error deleting data from DB for sender_id {sender_id}: {e}")
    finally:
        conn.commit()
        cursor.close()


def put_data_to_db(df: pd.DataFrame, sender_id: int) -> None:
    from technesis.config import logger

    with sqlite3.connect(DB_NAME) as conn:
        # Удаляем данные отправителя из базы данных
        remove_sender_data_from_db(conn, sender_id)
        # Сохраняем данные в базу данных
        df.to_sql("prices", conn, if_exists="append", index=False)
        logger.info("Data saved to DB")


def save_file(sender: int, file_name: str, file_content: bytes) -> str:
    try:
        sender_path = os.path.join(SAVE_PATH, str(sender))

        if not os.path.exists(sender_path):
            os.makedirs(sender_path)

        file_path = os.path.join(sender_path, file_name)
        with open(file_path, "wb") as f:
            f.write(file_content)

        return f"Файл '{file_name}' успешно сохранён."
    except Exception as e:
        return f"Ошибка при сохранении файла '{file_name}': {e}"


def get_average_prices_for_url(conn: sqlite3.Connection, url: str, sender_id: int) -> list:
    from technesis.config import logger

    try:
        cursor = conn.cursor()
        query = f"""
        SELECT title, AVG(price) FROM prices WHERE url LIKE '{url}%' AND sender_id = {sender_id} GROUP BY title
        """
        cursor.execute(query)
        avg_prices = cursor.fetchall()
        return avg_prices
    except Exception as e:
        logger.error(f"Ошибка при получении средней цены: {e}")
        return None
    finally:
        cursor.close()


def get_all_urls(conn: sqlite3.Connection, sender_id) -> set:
    from technesis.config import logger

    try:
        cursor = conn.cursor()
        query = "SELECT DISTINCT url FROM prices WHERE sender_id = ?"
        cursor.execute(query, (sender_id,))
        return {get_base_url(u[0]) for u in cursor.fetchall()}
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении всех URL: {e}")
        return set()
    finally:
        cursor.close()


def average_price_text(sender_id) -> str:
    from technesis.tasks import SITES_ALLOWED

    with sqlite3.connect(DB_NAME) as conn:
        text = ""
        urls = get_all_urls(conn, sender_id)
        for url in urls:
            if url in SITES_ALLOWED:
                text += f"URL: {url}\n"
                prices = get_average_prices_for_url(conn, url, sender_id)
                for price in prices:
                    text += f"Товар: {price[0]}, Средняя цена: {price[1]:.2f}\n"
        return text
