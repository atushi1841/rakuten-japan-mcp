"""Unit tests for rakuten_api: get_ranking parsing + search_items retry logic."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.rakuten_api import get_ranking, search_items


def test_import_modules():
    assert callable(search_items)
    assert callable(get_ranking)


def test_get_ranking_parses_items():
    """get_ranking should reshape the real IchibaItem/Ranking response into our dict shape.

    Live API shape: rank lives INSIDE Item, itemPrice is a string, accessKey required.
    """
    fake_json = {
        "Items": [
            {
                "Item": {
                    "rank": 1,
                    "itemName": "テスト商品",
                    "itemPrice": "1000",
                    "itemUrl": "https://item.example/1",
                    "shopName": "テストショップ",
                    "reviewAverage": "4.5",
                    "reviewCount": "10",
                    "mediumImageUrls": [{"imageUrl": "https://img.example/1.jpg"}],
                },
            },
            {
                "Item": {
                    "rank": 2,
                    "itemName": "商品2",
                    "itemPrice": "2,000",  # defensive: non-numeric parses to 0
                    "itemUrl": "https://item.example/2",
                    "shopName": "ショップ2",
                },
            },
        ]
    }

    async def _run():
        with patch("src.rakuten_api._get_json", new=AsyncMock(return_value=fake_json)):
            with patch.dict("os.environ", {
                "RAKUTEN_APP_ID": "APP", "RAKUTEN_ACCESS_KEY": "KEY"
            }):
                return await get_ranking(genre_id=101269, max_results=2)

    results = asyncio.run(_run())
    assert len(results) == 2
    assert results[0]["rank"] == 1
    assert results[0]["itemName"] == "テスト商品"
    assert results[0]["itemPrice"] == 1000
    assert results[0]["imageUrl"] == "https://img.example/1.jpg"
    # item with no image should yield None
    assert results[1]["imageUrl"] is None
    assert results[1]["itemPrice"] == 0


def test_get_ranking_requires_app_id():
    async def _run():
        with patch.dict("os.environ", {}, clear=True):
            return await get_ranking()

    with pytest.raises(ValueError):
        asyncio.run(_run())


def test_search_items_requires_keys():
    async def _run():
        with patch.dict("os.environ", {}, clear=True):
            return await search_items("PS5")

    with pytest.raises(ValueError):
        asyncio.run(_run())
