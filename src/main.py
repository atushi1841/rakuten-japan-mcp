"""
Rakuten Japan MCP — Main entry point.

Two modes:
1. Traditional Apify Actor: runs once, pushes data to dataset
2. MCP Server (Standby mode): hosts FastMCP server via uvicorn
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from apify import Actor

sys.path.insert(0, str(Path(__file__).parent))

from rakuten_api import search_items, get_ranking

logger = logging.getLogger(__name__)


async def run_actor(input_data: dict) -> None:
    """Run as a traditional Apify actor - search and push results to dataset."""
    keyword = input_data.get("searchKeyword", "")
    if not keyword:
        raise ValueError("searchKeyword is required")

    max_results = min(input_data.get("maxResults", 30), 100)
    min_price = input_data.get("minPrice")
    max_price = input_data.get("maxPrice")
    sort_by = input_data.get("sortBy")

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

        if len(items) < hits:
            break

        page += 1

    Actor.log.info(f"Pushed {total_pushed} items for keyword '{keyword}'")


async def run_mcp_server() -> None:
    """Run as MCP server (Standby mode) using uvicorn."""
    import uvicorn
    from server import get_server

    port = int(os.environ.get("APIFY_CONTAINER_PORT", "3000"))
    server = get_server()
    app = server.http_app(transport="streamable-http")

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server_instance = uvicorn.Server(config)

    Actor.log.info(f"MCP server starting on port {port}")
    await server_instance.serve()


async def run_ranking(input_data: dict) -> None:
    """Run as a traditional Apify actor - fetch and push ranking to dataset."""
    genre_id = input_data.get("genreId")
    ranking_type = input_data.get("rankingType", "item")
    max_results = min(input_data.get("maxResults", 30), 30)
    era = input_data.get("era")

    items = await get_ranking(
        genre_id=int(genre_id) if genre_id is not None else None,
        ranking_type=ranking_type,
        max_results=max_results,
        era=era,
    )
    for item in items:
        await Actor.push_data(item)
    Actor.log.info(f"Pushed {len(items)} ranking items (genre={genre_id}, type={ranking_type})")


async def main() -> None:
    """Main entry point. Auto-detects mode based on environment."""
    await Actor.init()

    try:
        input_data = await Actor.get_input() or {}

        # If input has searchKeyword, run as traditional actor
        if input_data.get("searchKeyword"):
            await run_actor(input_data)
        elif input_data.get("ranking", False):
            await run_ranking(input_data)
        else:
            # No search keyword = run as MCP server
            await run_mcp_server()

    except Exception as exc:
        Actor.log.exception("Execution failed")
        raise
    finally:
        await Actor.exit()
