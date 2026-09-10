import os
import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

RAKUTEN_SEARCH_ENDPOINT = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
RAKUTEN_RANKING_ENDPOINT = "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601"

# Genre IDs of common top-level categories (used as ranking shortcuts).
GENRE_HINTS = {
    "総合": None,
    "本・雑誌": 101269,
    "DVD": 101298,
    "CD": 101276,
    "ゲーム": 101031,
    "おもちゃ": 101347,
    "パソコン": 101190,
    "家電": 100371,
    "食品": 100227,
    "女性ファッション": 10037107,
    "メンズファッション": 10037108,
    "家具・インテリア": 101165,
    "スポーツ": 101204,
    " cosmetics": 101203,
    "情報・通信": 101190,
}


async def _get_json(url: str, params: dict, headers: dict) -> dict:
    """GET a Rakuten endpoint with simple 429 retry. Returns parsed JSON."""
    retries = 3
    delay = 1.0
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 429 and attempt < retries - 1:
                    logger.warning("Rate limited, retrying in %.1f seconds", delay)
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429 and attempt < retries - 1:
                logger.warning("Rate limited, retrying in %.1f seconds", delay)
                await asyncio.sleep(delay)
                delay *= 2
                continue
            raise
        return response.json()
    raise RuntimeError("Failed to fetch after retries")


def _app_id() -> str:
    app_id = os.environ.get("RAKUTEN_APP_ID")
    if not app_id:
        raise ValueError("RAKUTEN_APP_ID environment variable must be set")
    return app_id


async def search_items(
    keyword: str,
    max_results: int = 30,
    page: int = 1,
    min_price: int | None = None,
    max_price: int | None = None,
    sort: str | None = None,
) -> list[dict]:
    """
    Search Rakuten Ichiba items using the official API.
    Returns a list of product dicts with keys:
      itemName, itemPrice, itemUrl, shopName, reviewAverage, reviewCount, imageUrl
    """
    app_id = _app_id()
    access_key = os.environ.get("RAKUTEN_ACCESS_KEY")
    if not access_key:
        raise ValueError("RAKUTEN_ACCESS_KEY environment variable must be set")

    params: dict[str, str | int] = {
        "applicationId": app_id,
        "accessKey": access_key,
        "keyword": keyword,
        "hits": max_results,
        "page": page,
    }
    if min_price is not None:
        params["minPrice"] = min_price
    if max_price is not None:
        params["maxPrice"] = max_price
    if sort is not None:
        params["sort"] = sort

    headers = {
        "Origin": "https://api.apify.com",
        "Referer": "https://api.apify.com/",
    }
    data = await _get_json(RAKUTEN_SEARCH_ENDPOINT, params, headers)
    raw_items = data.get("Items", [])
    results: list[dict] = []
    for raw_item in raw_items:
        item = raw_item.get("Item", {})
        if not item:
            continue
        medium_images = item.get("mediumImageUrls", [])
        image_url = medium_images[0].get("imageUrl") if medium_images else None
        results.append(
            {
                "itemName": item.get("itemName", ""),
                "itemPrice": item.get("itemPrice", 0),
                "itemUrl": item.get("itemUrl", ""),
                "shopName": item.get("shopName", ""),
                "reviewAverage": item.get("reviewAverage", 0.0),
                "reviewCount": item.get("reviewCount", 0),
                "imageUrl": image_url,
            }
        )
    return results


async def get_ranking(
    genre_id: int | None = None,
    era: str | None = None,
    ranking_type: str = "item",
    max_results: int = 30,
) -> list[dict]:
    """
    Get the current Rakuten Ichiba ranking using the official IchibaRanking API.

    Args:
        genre_id: restrict to a genre (e.g. 101269=本・雑誌). None = overall ranking.
        era: past-ranking era, format 'YYYYMMDD' (e.g. '20190601'). None = current.
        ranking_type: 'item' (default), 'male', or 'female'.
        max_results: number of ranked items to return (max 30 per call).

    Returns a list of dicts with keys:
      rank, itemName, itemPrice, itemUrl, shopName, reviewAverage, reviewCount, imageUrl
    """
    app_id = _app_id()
    access_key = os.environ.get("RAKUTEN_ACCESS_KEY")
    if not access_key:
        raise ValueError("RAKUTEN_ACCESS_KEY environment variable must be set")

    params: dict[str, str | int] = {
        "applicationId": app_id,
        "accessKey": access_key,
        "rankingType": ranking_type,
        "hits": max_results,
    }
    if genre_id is not None:
        params["genreId"] = int(genre_id)
    if era is not None:
        params["era"] = era

    headers = {
        "Origin": "https://api.apify.com",
        "Referer": "https://api.apify.com/",
    }
    data = await _get_json(RAKUTEN_RANKING_ENDPOINT, params, headers)
    raw_items = data.get("Items", [])
    results: list[dict] = []
    for raw_item in raw_items:
        item = raw_item.get("Item", {})
        if not item:
            continue
        medium_images = item.get("mediumImageUrls", [])
        image_url = medium_images[0].get("imageUrl") if medium_images else None
        rank = raw_item.get("rank", item.get("rank"))
        try:
            price = int(str(item.get("itemPrice", 0)))
        except (TypeError, ValueError):
            price = 0
        results.append(
            {
                "rank": rank,
                "itemName": item.get("itemName", ""),
                "itemPrice": price,
                "itemUrl": item.get("itemUrl", ""),
                "shopName": item.get("shopName", ""),
                "reviewAverage": item.get("reviewAverage", 0.0),
                "reviewCount": item.get("reviewCount", 0),
                "imageUrl": image_url,
            }
        )
    return results
