# Rakuten Japan MCP — 楽天市場商品検索

**Search Rakuten Ichiba (楽天市場) products via the official Rakuten API.**  
Extract item names, prices, URLs, shop info, reviews, and images in clean structured JSON.

[![Apify Store](https://img.shields.io/badge/Apify-Store-blue)](https://apify.com/fruitful_quintessence/rakuten-japan-mcp)

---

## 🚀 What This Does

This actor wraps the official [Rakuten Ichiba Item Search API](https://webservice.rakuten.co.jp/documentation/ichiba-item-search) and makes it available as:

1. **A traditional Apify actor** — run it from the Apify Console, API, or schedule
2. **An MCP server** — connect AI agents (Claude, Cursor, ChatGPT) to search Rakuten in real-time

**Why use this?** Rakuten is Japan's largest e-commerce platform with millions of products. This actor gives you programmatic access to product data without scraping HTML or managing proxies.

---

## 🔧 Usage

### As an Apify Actor

1. Go to the actor page on Apify Store
2. Enter a search keyword (e.g., "ポケモン", "フィギュア", "PS5")
3. Set optional filters: max results, price range, sort order
4. Run and get results as JSON, CSV, or XLSX

**Input Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `searchKeyword` | string | — | Keyword to search (required) |
| `maxResults` | int | 30 | Max results (1-100) |
| `minPrice` | int | — | Minimum price in JPY (optional) |
| `maxPrice` | int | — | Maximum price in JPY (optional) |
| `sortBy` | select | standard | Sort order |

### As an MCP Server

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "rakuten-japan": {
      "command": "npx",
      "args": [
        "-y",
        "@apify/mcp-server",
        "--actor", "fruitful_quintessence/rakuten-japan-mcp"
      ]
    }
  }
}
```

Available tools:
- `search_rakuten(keyword, max_results, min_price, max_price)` — Search products
- `get_actor_info()` — List available tools

---

## 📋 Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `itemName` | string | Product name (Japanese) |
| `itemPrice` | int | Current price in JPY |
| `itemUrl` | string | Product page URL |
| `shopName` | string | Seller shop name |
| `reviewAverage` | float | Average review rating |
| `reviewCount` | int | Number of reviews |
| `imageUrl` | string | Product image URL |

---

## 💰 Pricing

Pay per event:
- **$0.005/run** — Actor start
- **$0.001/search** — Per search query
- **$0.00001/result** — Per dataset item stored

Free plan available for testing.

---

## 🏗 Architecture

```
User Input → Rakuten Ichiba API (official, free)
                  ↓
            JSON Response
                  ↓
            Structured Output → Apify Dataset
```

- **100% legal** — Uses the official Rakuten Web Service API (free, commercial use allowed)
- **No proxies needed** — Direct API calls, no HTML scraping
- **Rate limited** — Respects API limits with automatic retry + backoff

---

## 🔧 Development

```bash
pip install -r requirements.txt

# Set API keys
export RAKUTEN_APP_ID="your-app-id"
export RAKUTEN_ACCESS_KEY="your-access-key"

# Run locally
python3 -m src

# Deploy to Apify
npx apify push
```

---

## ⚠️ Requirements

- Rakuten Web Service API credentials (free — register at https://webservice.rakuten.co.jp/)
- The API requires an `Origin` header matching your registered domain

---

## 📝 License

MIT
