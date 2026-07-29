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
    """Search products on Rakuten Ichiba (楽天市場) and return matching items."""
    # Charge for this platform‑powered execution
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
async def search_rakuten_ranking(genre_id: str | None = None) -> list[dict[str, Any]]:
    """Retrieve the current Rakuten Ichiba ranking (stub — API not yet integrated)."""
    from apify import Actor

    if Actor.is_initialized():
        await Actor.charge("rakuten-search")

    # TODO: implement real ranking endpoint when required
    return []


@mcp.tool()
async def get_actor_info() -> dict[str, Any]:
    """Return information about the available tools in this MCP server."""
    return {
        "name": "Rakuten Japan MCP",
        "tools": ["search_rakuten", "search_rakuten_ranking", "get_actor_info"],
        "version": "0.1",
    }


if __name__ == "__main__":
    mcp.run()
