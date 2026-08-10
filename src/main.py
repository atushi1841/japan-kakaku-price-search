"""
Japan Kakaku Price Search — 価格.com のキーワード価格検索.

日本の最大級価格比較サイト「価格.com」から商品名・最安価格・ショップ数を
キーワード検索で収集し、横断価格データを出力します。
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

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
