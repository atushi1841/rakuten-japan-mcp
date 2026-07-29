from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).parent))

from rakuten_api import search_items

mcp = FastMCP("Rakuten Japan MCP")


@mcp.tool()
async def search_rakuten(
    keyword: str,
    max_results: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[dict[str, Any]]:
    """Search products on Rakuten Ichiba (楽天市場) and return matching items.

    Args:
        keyword: Search keyword (e.g. "ポケモン", "フィギュア", "PS5")
        max_results: Maximum number of results to return (default 10, max 30)
        min_price: Minimum price in JPY (optional)
        max_price: Maximum price in JPY (optional)
    """
    # Charge for this platform execution
    from apify import Actor

    if Actor.is_initialized():
        await Actor.charge("rakuten-search")

    items = await search_items(
        keyword=keyword,
        max_results=max_results,
        min_price=min_price,
        max_price=max_price,
    )
    return items


@mcp.tool()
async def get_actor_info() -> dict[str, Any]:
    """Return information about the available tools in this MCP server."""
    return {
        "name": "Rakuten Japan MCP",
        "description": "Search Rakuten Ichiba (楽天市場) products via the official API",
        "tools": ["search_rakuten", "get_actor_info"],
        "version": "0.1",
        "pricing": "$0.005/run + $0.001/search",
    }


if __name__ == "__main__":
    mcp.run()
