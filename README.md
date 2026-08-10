# Japan Kakaku Price Search — 価格.com Price Lookup

**Search Japan's #1 price comparison site 価格.com (Kakaku) and get product name, lowest price, shop count & review score in one dataset.**

Kakaku.com aggregates prices from **thousands of Japanese online stores** (Amazon, Yodobashi, Bic Camera, Rakuten, Yahoo Shopping, etc.) for every product category — electronics, smartphones, cameras, PC parts, home appliances, games, and more.

> 🇨🇳 中文版: [日本价格搜索](https://apify.com/fruitful_quintessence) / 🇰🇷 한국어판: [일본 가격 검색](https://apify.com/fruitful_quintessence)

## Why this is useful

- **Market price research** — get the current lowest price + shop count for any product in Japan
- **Price comparison** — one keyword → all competing products with prices side by side
- **Product intelligence** — review scores + shop counts reveal demand signals
- **Cross-border trading** — find price gaps between Japanese retail and international markets

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `keyword` | string | `iPhone` | Search keyword (e.g. iPhone, 一眼レフ, PS5, RTX 5080, カメラ) |
| `maxItems` | integer | 100 | Max items to collect |
| `maxPages` | integer | 2 | Max search result pages |

## Output Sample

```json
{
  "productId": "kakaku-iPhone 17e-0",
  "title": "iPhone 17e",
  "maker": "Apple",
  "price": 101799,
  "priceType": "端末価格",
  "shopCount": 149,
  "review": "4.25 (44)",
  "specs": ["6.1インチ", "48MP Fusionカメラ", "顔認証", "Apple Pay", "耐水・防水", "eSIM"],
  "productUrl": "https://kakaku.com/keitai/smartphone/model/M0000001194/",
  "keyword": "iPhone",
  "source": "kakaku",
  "shop": "価格.com"
}
```

## Use Cases

- **Price monitoring** — schedule daily runs to track price drops for specific products
- **Market research** — analyze the competitive landscape across all product categories
- **Import/export arbitrage** — identify products where Japanese prices differ from global markets
- **Review mining** — product ratings and review counts for purchase decisions

## Pricing

Pay-per-event — **$0.00005/run start + $0.002/item**.

## Data Source

Public search results from Kakaku.com (product name, lowest price, shop count, review score, specs).

## Connect

Connect to your workflow via **Apify Connectors**: Google Sheets, Slack, or webhooks — automate price monitoring without code.
