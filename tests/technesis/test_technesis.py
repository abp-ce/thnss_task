import os
import sqlite3

import pandas as pd

import pytest

from src.technesis.parsers import parse_price_for_ozon
from src.technesis.tasks import SITES_ALLOWED
from src.technesis.utils import (
    get_all_urls,
    get_average_prices_for_url,
    get_base_url,
    prepare_data,
)


TEST_DB_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'test.db'))
SENDER_ID = 1234567890

TEST_DATA = [
    {
        "title": "Xiaomi Mi Smart Scale 2",
        "url": "https://www.wildberries.ru/catalog/208758128/detail.aspx",
        "xpath": "/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[14]/div/div[1]/div[1]/div/div/div/p/span/ins",  # noqa E501
    },
    {
        "title": "Xiaomi Mi Smart Scale 2",
        "url": f"file://{os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'example.html'))}",
        "xpath": "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[5]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/span[1]",  # noqa E501
    },
]


def test_get_base_url():
    url = TEST_DATA[0]["url"]
    base_url = get_base_url(url)
    assert base_url == "https://www.wildberries.ru"


@pytest.mark.asyncio
async def test_fetch_url():
    price = await parse_price_for_ozon(TEST_DATA[1]["url"], TEST_DATA[1]["xpath"])
    if price is not None:
        assert price == 1727


def test_prepare_data():
    df = pd.DataFrame(TEST_DATA)
    prepared_df = prepare_data(df, SENDER_ID)
    assert "url" in prepared_df.columns
    assert "price" in prepared_df.columns
    assert "title" in prepared_df.columns
    assert "sender_id" in prepared_df.columns
    assert len(prepared_df) == len(TEST_DATA)


def test_average_price():
    with sqlite3.connect(TEST_DB_NAME) as conn:
        urls = get_all_urls(conn, SENDER_ID)
        for url in urls:
            if url in SITES_ALLOWED:
                prices = get_average_prices_for_url(conn, url, SENDER_ID),
                for price in prices:
                    title, avg_price = price
                    if title == "Xiaomi Mi Smart Scale 2":
                        assert avg_price == 2134.8
                    elif title == "Xiaomi Body Composition Scale S400":
                        assert avg_price == 1727.0
