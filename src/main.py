"""
Japan Kakaku Price Search — 価格.com のキーワード価格検索.

日本の最大級価格比較サイト「価格.com」から商品名・最安価格・ショップ数を
キーワード検索で収集し、横断価格データを出力します。
"""

from __future__ import annotations

import asyncio
import datetime
import json
import sys
import unicodedata
from pathlib import Path


def _norm_key(text: str) -> str:
    """Normalize text for case-insensitive comparison (NFC + casefold)."""
    return unicodedata.normalize("NFC", text).casefold()


sys.path.insert(0, str(Path(__file__).parent))

try:
    from apify import Actor
except ImportError:
    Actor = None

from sources.kakaku import search_kakaku


async def run(actor_input: dict) -> list[dict]:
    keyword = str(actor_input.get("keyword", "iPhone")).strip()
    max_items = int(actor_input.get("maxItems", 100))
    max_pages = int(actor_input.get("maxPages", 2))
    stats_mode = actor_input.get("statsMode", False)

    import httpx

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        results = await search_kakaku(
            client,
            keyword=keyword,
            max_pages=max_pages,
            max_items=max_items,
        )

    if stats_mode:
        stats_filter = str(actor_input.get("statsKeyword", "")).strip()
        filtered_items = []
        for item in results:
            title = str(item.get("title", ""))
            if stats_filter and _norm_key(stats_filter) not in _norm_key(title):
                continue
            filtered_items.append(item)

        prices = []
        for item in filtered_items:
            raw_price = item.get("price")
            try:
                price = int(raw_price)
            except (TypeError, ValueError):
                continue
            prices.append(price)

        prices_sorted = sorted(prices)
        count = len(prices_sorted)
        if count == 0:
            price_min = price_max = price_avg = price_median = None
        else:
            price_min = prices_sorted[0]
            price_max = prices_sorted[-1]
            price_avg = int(sum(prices_sorted) / count)
            mid = count // 2
            if count % 2 == 1:
                price_median = prices_sorted[mid]
            else:
                price_median = int((prices_sorted[mid - 1] + prices_sorted[mid]) / 2)

        sample_items = []
        for item in filtered_items[:3]:
            sample_items.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "detailUrl": item.get("detailUrl"),
                "shop": item.get("shop"),
            })

        stats_result = {
            "statsType": "japan-kakaku-price",
            "keyword": keyword,
            "count": count,
            "priceMin": price_min,
            "priceMax": price_max,
            "priceAvg": price_avg,
            "priceMedian": price_median,
            "sampleItems": sample_items,
            "collectedAt": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        if Actor is not None:
            await Actor.push_data(stats_result)
            print(f"Collected stats for '{keyword}': {count} items")
        else:
            print(json.dumps(stats_result, ensure_ascii=False))
        return []

    if Actor is not None:
        for item in results:
            await Actor.push_data(item)
        print(f"Collected {len(results)} items for '{keyword}'")
    return results


async def main() -> None:
    if Actor is not None:
        async with Actor:
            actor_input = await Actor.get_input() or {}
            await run(actor_input)
    else:
        raw = sys.stdin.read().strip()
        actor_input = json.loads(raw) if raw else {}
        results = await run(actor_input)
        for item in results:
            print(json.dumps(item, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
