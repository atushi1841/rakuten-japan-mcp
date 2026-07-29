import asyncio
import logging
from apify import Actor

from .rakuten_api import search_items

logger = logging.getLogger(__name__)


async def main() -> None:
    """Apify Actor entry point for Rakuten Ichiba search."""
    await Actor.init()

    try:
        user_input = await Actor.get_input() or {}
        keyword = user_input.get("searchKeyword", "")
        if not keyword:
            raise ValueError("The input 'searchKeyword' is required.")

        max_results = min(user_input.get("maxResults", 30), 100)
        min_price = user_input.get("minPrice")
        max_price = user_input.get("maxPrice")
        sort_by = user_input.get("sortBy")  # e.g. "+itemPrice", "-itemPrice", "standard", "reviewCount"

        page = 1
        remaining = max_results
        total_pushed = 0

        while remaining > 0:
            hits = min(remaining, 30)
            items = await search_items(
                keyword=keyword,
                max_results=hits,
                page=page,
                min_price=min_price,
                max_price=max_price,
                sort=sort_by,
            )

            if not items:
                break

            for item in items:
                await Actor.push_data(item)
                total_pushed += 1
                remaining -= 1

            # If the API returned fewer items than requested, we are done
            if len(items) < hits:
                break

            page += 1

        Actor.log.info(f"Successfully pushed {total_pushed} items to the dataset.")

    except Exception as exc:
        Actor.log.exception("Error during execution")
        raise
    finally:
        await Actor.exit()
