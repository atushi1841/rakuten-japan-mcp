# Rakuten Japan MCP — 楽天市場商品検索・ランキング

**Search Rakuten Ichiba (楽天市場) products and fetch the current ranking via the official Rakuten APIs.**  
Extract item names, prices, URLs, shop info, reviews, and images in clean structured JSON.

[![Apify Store](https://img.shields.io/badge/Apify-Store-blue)](https://apify.com/fruitful_quintessence/rakuten-japan-mcp)

---

## 🚀 What This Does

This actor wraps the official Rakuten APIs and makes them available two ways:

1. **A traditional Apify actor** — run it from the Apify Console, API, or schedule
2. **An MCP server** — connect AI agents (Claude, Cursor, ChatGPT) to query Rakuten in real-time

**Two data access modes:**
- **Product search** — `IchibaItem/Search` official API (keyword search)
- **Ranking** — `IchibaItem/Ranking` official API (what's hot, genre ranking, historical eras)

**Why use this?** Rakuten is Japan's largest e-commerce platform with millions of products. This actor gives you programmatic access to product and ranking data without scraping HTML or managing proxies — both via TOS-compliant official APIs.

---

## 🔧 Usage

### As an Apify Actor

**1. Product Search** — set `searchKeyword` (e.g. "ポケモン", "フィギュア", "PS5") and optional filters.

**2. Ranking** — set `ranking` to `true`, optionally narrow with `genreId`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ranking` | boolean | false | Set true to fetch ranking instead of search |
| `genreId` | integer | — | Restrict to genre (e.g. 101269=本・雑誌, 101347=おもちゃ) |
| `rankingType` | select | item | `item`, `male`, or `female` |
| `era` | string | — | Past-ranking era `YYYYMMDD` (e.g. `20190601`) |
| `maxResults` | int | 30 | Max results (ranking max 30 per call) |

### As an MCP Server

Connect any MCP-compatible client to the actor's standby endpoint.

**Tools:**
- **`search_rakuten`** — keyword product search, returns title/price/URL/shop/review/image
- **`search_rakuten_ranking`** — current Rakuten ranking (genre / male / female / historical era)
- **`get_actor_info`** — list of tools and pricing

---

## 🧹 Official API Details

- **Search:** `https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701`
- **Ranking:** `https://app.rakuten.co.jp/services/api/IchibaRanking/Ranking/20220601`

Search requires `RAKUTEN_APP_ID` **and** `RAKUTEN_ACCESS_KEY`; ranking requires only `RAKUTEN_APP_ID`. These are `Secret` environment variables set on the Apify actor.

---

## 🧪 Tests & Type Checking

```bash
python -m pytest tests/ -v
python -m mypy src/ --strict
```

Deploy happens automatically on push to `master`/`main` via GitHub Actions.

---

## 🔒 Pricing (pay-per-event)

- `rakuten-search`: $0.001 / search
- `rakuten-ranking`: $0.001 / ranking
