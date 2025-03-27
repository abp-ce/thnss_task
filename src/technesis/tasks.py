import pandas as pd

from technesis.parsers import parse_price_for_ozon
from technesis.utils import (
    get_base_url,
    prepare_data,
    put_data_to_db,
)

SITES_ALLOWED = {
    "https://www.ozon.ru": parse_price_for_ozon,
}


async def process_file_data(df: pd.DataFrame, sender_id: int) -> str:
    from technesis.config import logger

    logger.info("...prosessing data...")
    df = prepare_data(df, sender_id)
    for index, row in df.iterrows():
        if (base_url := get_base_url(row["url"])) in SITES_ALLOWED:
            logger.info(f"Processing {base_url}...")
            parser = SITES_ALLOWED[base_url]
            price = await parser(row["url"], row["xpath"])
            df.at[index, "price"] = price

    put_data_to_db(df, sender_id)

    logger.info("...data processed...")

    return "Данные успешно обработаны и сохранены в базе данных."
