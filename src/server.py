"""
Rakuten Japan MCP Server — FastMCP server factory.

Exposes Rakuten Ichiba search as AI agent tools.
Compatible with Apify Standby mode (uvicorn + APIFY_CONTAINER_PORT).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).parent))

from rakuten_api import search_items, get_ranking


def get_server() -> FastMCP:
    """Create and return the FastMCP server instance."""
    server = FastMCP("Rakuten Japan MCP", "0.1.0")

    @server.tool()
    async def search_rakuten(
        keyword: str,
        max_results: int = 10,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> dict:
        """Search products on Rakuten Ichiba (楽天市場).

        Args:
            keyword: Search keyword in Japanese (e.g. "ポケモン", "フィギュア", "PS5")
            max_results: Maximum items to return (default 10, max 30)
            min_price: Minimum price in JPY (optional)
            max_price: Maximum price in JPY (optional)
        """
        from apify import Actor

        if Actor.is_initialized():
            await Actor.charge("rakuten-search")

        items = await search_items(
            keyword=keyword,
            max_results=max_results,
            min_price=min_price,
            max_price=max_price,
        )

        if not items:
            return {
                "type": "text",
                "text": f"「{keyword}」の検索結果は0件でした。",
                "structuredContent": {"keyword": keyword, "count": 0, "items": []},
            }

        text_lines = [f"**楽天市場 検索結果: {keyword}** ({len(items)}件)", ""]
        for i, item in enumerate(items[:10], 1):
            name = item.get("itemName", "?")[:50]
            price = f"¥{item['itemPrice']:,}" if item.get("itemPrice") else "?"
            url = item.get("itemUrl", "")
            shop = item.get("shopName", "")
            text_lines.append(f"{i}. **{name}** — {price} ({shop})")
            if url:
                text_lines.append(f"   {url}")

        return {
            "type": "text",
            "text": "\n".join(text_lines),
            "structuredContent": {
                "keyword": keyword,
                "count": len(items),
                "items": items,
            },
        }

    @server.tool()
    async def search_rakuten_ranking(
        genre_id: int | None = None,
        ranking_type: str = "item",
        max_results: int = 10,
        era: str | None = None,
    ) -> dict:
        """Get the current Rakuten Ichiba ranking (楽天市場 ランキング) via the official IchibaRanking API.

        Useful for trend research, "what's hot" discovery, and resale/arbitrage signals
        without any keyword search.

        Args:
            genre_id: Restrict ranking to a genre (e.g. 101269=本・雑誌, 101347=おもちゃ,
                101031=ゲーム, 100371=家電). None (default) returns the overall ranking.
            ranking_type: "item" (default), "male", or "female".
            max_results: Number of ranked items to return (default 10, max 30).
            era: Past-ranking era as 'YYYYMMDD' (e.g. "20190601"). None = current ranking.
        """
        from apify import Actor

        if Actor.is_initialized():
            await Actor.charge("rakuten-ranking")

        items = await get_ranking(
            genre_id=genre_id,
            ranking_type=ranking_type,
            max_results=max_results,
            era=era,
        )

        if not items:
            return {
                "type": "text",
                "text": "ランキングの取得結果は0件でした。",
                "structuredContent": {
                    "genreId": genre_id,
                    "rankingType": ranking_type,
                    "count": 0,
                    "items": [],
                },
            }

        scope = f"genre {genre_id}" if genre_id else "総合"
        text_lines = [f"**楽天市場 ランキング: {scope}** ({len(items)}件)", ""]
        for item in items:
            rank = item.get("rank", "?")
            name = item.get("itemName", "?")[:50]
            price = f"¥{item['itemPrice']:,}" if item.get("itemPrice") else "?"
            text_lines.append(f"{rank}. **{name}** — {price}")

        return {
            "type": "text",
            "text": "\n".join(text_lines),
            "structuredContent": {
                "genreId": genre_id,
                "rankingType": ranking_type,
                "count": len(items),
                "items": items,
            },
        }

    @server.tool()
    async def get_actor_info() -> dict:
        """Get information about available tools and pricing."""
        return {
            "type": "text",
            "text": (
                "**Rakuten Japan MCP** v0.1\n"
                "楽天市場の商品を公式APIで検索します。\n\n"
                "**Tools:**\n"
                "- search_rakuten: キーワード商品検索\n"
                "- search_rakuten_ranking: 楽天市場ランキング取得\n"
                "- get_actor_info: この情報\n\n"
                "**Pricing:** $0.005/run + $0.001/search (or ranking)"
            ),
            "structuredContent": {
                "name": "Rakuten Japan MCP",
                "version": "0.1",
                "tools": ["search_rakuten", "search_rakuten_ranking", "get_actor_info"],
                "pricing": "$0.005/run + $0.001/search (or ranking)",
            },
        }

    return server
