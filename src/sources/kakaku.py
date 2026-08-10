"""
価格.com (kakaku.com) キーワード検索スクレイパー.

検索ページ: https://search.kakaku.com/{keyword}/
エンコーディング: cp932 (Shift_JIS) 必須
商品カード構造 (p-resultItem):
  商品名: <a class="p-item_name">iPhone 17e</a>（メーカー: Apple）
  最安価格: <p class="p-item_price"><em class="p-item_priceNum">101,799～</em></p>
  価格種別: <p class="p-item_price_type">端末価格</p>
  レビュー: 4.25 (44)
  ショップ数: 149 件
  仕様: <li class="p-item_spec_data_type2">6.1インチ</li>
  リンク: <a class="p-resultItem_btnLink" href="https://kakaku.com/.../M0000001194/">
"""

from __future__ import annotations

import asyncio
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://search.kakaku.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def fetch_page(client: httpx.AsyncClient, url: str, max_retries: int = 3) -> Optional[str]:
    for attempt in range(max_retries):
        try:
            resp = await client.get(url, headers=HEADERS, follow_redirects=True)
            if resp.status_code == 200:
                # 価格.com は cp932 (Shift_JIS)
                resp.encoding = "cp932"
                return resp.text
            if resp.status_code in (403, 429):
                await asyncio.sleep(3 * (attempt + 1))
                continue
            return None
        except httpx.HTTPError:
            await asyncio.sleep(2 * (attempt + 1))
    return None


def _clean_price(raw: str) -> Optional[int]:
    """'101,799～' → 101799 / '¥8,980' → 8980"""
    m = re.search(r"([\d,]+)", raw)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def parse_items(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for item in soup.select(".p-resultItem"):
        # 商品名・メーカー
        name_el = item.select_one(".p-item_name, a.p-item_name")
        title = name_el.get_text(" ", strip=True) if name_el else ""
        maker_el = item.select_one(".p-item_maker")
        maker = maker_el.get_text(" ", strip=True) if maker_el else ""
        # 価格
        price_el = item.select_one(".p-item_priceNum")
        price = _clean_price(price_el.get_text(" ", strip=True)) if price_el else None
        price_type_el = item.select_one(".p-item_price_type")
        price_type = price_type_el.get_text(" ", strip=True) if price_type_el else ""
        # レビュー（4.25 (44)）
        review = ""
        score_el = item.select_one(".p-item_star_rating_num")
        count_el = item.select_one(".p-item_star_count")
        if score_el:
            score = score_el.get_text(" ", strip=True)
            count = count_el.get_text(" ", strip=True) if count_el else ""
            review = f"{score} {count}".strip()
        # ショップ数（N件）
        shops = 0
        m = re.search(r"(\d+)\s*件", item.get_text(" ", strip=True))
        if m:
            shops = int(m.group(1))
        # 仕様
        specs = [s.get_text(" ", strip=True) for s in item.select(".p-item_spec_data_type2")][:6]
        # リンク
        link = ""
        link_el = item.select_one("a.p-resultItem_btnLink, a[href*='kakaku.com/']")
        if link_el:
            href = str(link_el.get("href", "") or "")
            if href.startswith("/"):
                link = "https://kakaku.com" + href
            elif href.startswith("http"):
                link = href
        if not title and price is None:
            continue
        items.append({
            "productId": f"kakaku-{title}-{len(items)}",
            "title": title,
            "maker": maker,
            "price": price,
            "priceType": price_type,
            "shopCount": shops,
            "review": review,
            "specs": specs,
            "productUrl": link or BASE_URL,
            "source": "kakaku",
            "shop": "価格.com",
        })
    return items


async def search_kakaku(
    client: httpx.AsyncClient,
    keyword: str = "iPhone",
    max_pages: int = 2,
    max_items: int = 100,
) -> list[dict]:
    import urllib.parse
    kw = urllib.parse.quote(keyword.strip())
    base = f"{BASE_URL}/{kw}/"
    results: list[dict] = []
    page = 1
    while page <= max_pages and len(results) < max_items:
        url = base if page == 1 else f"{base}?page={page}"
        html = await fetch_page(client, url)
        if not html:
            break
        items = parse_items(html)
        if not items:
            break
        for it in items:
            if len(results) >= max_items:
                break
            it["keyword"] = keyword
            it["scrapedAt"] = __import__("datetime").datetime.now().isoformat() + "Z"
            results.append(it)
        if f"page={page+1}" not in html:
            break
        page += 1
        await asyncio.sleep(0.5)
    return results
