# Rakuten Japan MCP — 楽天市場商品検索

Search Rakuten Ichiba (楽天市場), Japan's largest e-commerce platform, via the official Rakuten API. Extract product names, prices, URLs, shop info, review counts, ratings, and images. Available as an Apify actor and an MCP server for AI agents.

[![Apify Store](https://img.shields.io/badge/Apify-Store-blue)](https://apify.com/fruitful_quintessence/rakuten-japan-mcp)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## What This Does

This actor wraps the official [Rakuten Ichiba Item Search API](https://webservice.rakuten.co.jp/documentation/ichiba-item-search) and makes it available as:

1. **A traditional Apify actor** — run from the Apify Console, API, or schedule
2. **An MCP server** — connect AI agents (Claude, Cursor, ChatGPT) to search Rakuten in real-time

**Why use this?** Rakuten is Japan's largest e-commerce platform with millions of products. This gives you programmatic access to product data without scraping HTML or managing proxies. 100% legal — uses the official API.

## Output Sample

```json
[
  {
    "itemName": "ポケモンカード 拡張パック",
    "itemPrice": 1800,
    "shopName": "カードショップ○○",
    "itemUrl": "https://item.rakuten.co.jp/...",
    "reviewCount": 45,
    "reviewAverage": 4.2,
    "mediumImageUrls": [
      { "imageUrl": "https://thumbnail.image.rakuten.co.jp/..." }
    ],
    "shopOfTheYearFlag": false,
    "genreId": "112345"
  }
]
```

## Input

```json
{
  "keyword": "ポケモン",
  "maxResults": 30,
  "genreId": "",
  "minPrice": "",
  "maxPrice": ""
}
```

Parameters:
- `keyword` (required) — Search term (Japanese supported)
- `maxResults` (optional, default: 30, max: 100) — Results per search
- `genreId` (optional) — Filter by Rakuten genre/category ID
- `minPrice` / `maxPrice` (optional) — Price range filter (JPY)

## MCP Usage

### Claude Desktop

```json
{
  "mcpServers": {
    "rakuten-japan": {
      "url": "https://fruitful-quintessence--rakuten-japan-mcp.apify.actor/mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add rakuten-japan \
  --transport http \
  https://fruitful-quintessence--rakuten-japan-mcp.apify.actor/mcp
```

## Use Cases

- **Price comparison agent** — "Find the cheapest Nintendo Switch game on Rakuten"
- **Product research** — "Show me top-rated anime figure shops with reviews"
- **Inventory monitoring** — Schedule daily runs to track price changes
- **AI shopping assistant** — Let AI agents search Rakuten before making purchase recommendations

## Pricing

- **$0.005 per actor start** + **$0.001 per search** + **$0.00001 per result item**
- Typical 30-item search: ~**$0.006** total
- You only pay for what you use — no monthly subscription

## FAQ

**Do I need a Rakuten API key?** No. The actor uses the creator's API credentials internally. You just search.

**Is this legal?** Yes. This uses the official Rakuten Web Service API with proper attribution.

**Can I use this from an AI agent like Claude?** Yes. Connect via MCP endpoint. The server speaks Streamable HTTP at `/mcp`.

**How many results can I get per search?** Up to 100 items per query (Rakuten API limit).

## Limitations

- Results are limited to what the Rakuten Ichiba Item Search API returns
- Affiliate links require your own Rakuten affiliate ID
- The API has rate limits; excessive queries are throttled

## Changelog

- v0.1.7 (2026-07-29): Improved README with output samples, MCP usage guide, use cases
- v0.1.6 (2026-07-29): PPE pricing configured ($0.005/start + $0.001/search)
- v0.1.0 (2026-07-29): Initial release with Rakuten Ichiba search via official API
