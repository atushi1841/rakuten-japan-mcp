import os
import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

RAKUTEN_ENDPOINT = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"


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
    app_id = os.environ.get("RAKUTEN_APP_ID")
    access_key = os.environ.get("RAKUTEN_ACCESS_KEY")
    if not app_id or not access_key:
        raise ValueError("RAKUTEN_APP_ID and RAKUTEN_ACCESS_KEY environment variables must be set")

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
    retries = 3
    delay = 1.0
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(RAKUTEN_ENDPOINT, params=params, headers=headers)
                if response.status_code == 429:
                    if attempt < retries - 1:
                        logger.warning("Rate limited, retrying in %.1f seconds", delay)
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    else:
                        response.raise_for_status()
                else:
                    response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429 and attempt < retries - 1:
                logger.warning("Rate limited, retrying in %.1f seconds", delay)
                await asyncio.sleep(delay)
                delay *= 2
                continue
            raise

        data = response.json()
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
    # should not reach
    raise RuntimeError("Failed to fetch after retries")
