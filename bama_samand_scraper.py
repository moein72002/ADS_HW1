#!/usr/bin/env python3
"""
Scrape Samand car listings from bama.ir matching the HW1 bonus requirements.

Outputs the first 50 listings (year > 1385) with price, mileage, color,
production year, transmission type, and description into data/samand_listings.xlsx.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup
import xlsxwriter

BASE_URL = "https://bama.ir/car/samand"
LISTINGS_PER_REQUEST = 25
MIN_YEAR = 1385
OUTPUT_PATH = Path("data/samand_listings.xlsx")
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fa;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://bama.ir/",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
}

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
YEAR_RE = re.compile(r"(13\d{2}|14\d{2})")
MILEAGE_RE = re.compile(r"(\d[\d\.,]*)\s*(?:کیلومتر|km)", flags=re.IGNORECASE)
PRICE_RE = re.compile(r"(\d[\d\.,]*)\s*(?:تومان|ریال|﷼)?", flags=re.IGNORECASE)


@dataclass
class SamandListing:
    title: str
    price: Optional[int]
    mileage_km: Optional[int]
    color: Optional[str]
    production_year: int
    transmission: Optional[str]
    description: str
    url: str


def normalize_digits(text: str) -> str:
    """Convert Persian digits and strip commas/whitespace."""
    return re.sub(r"[^\d]", "", text.translate(PERSIAN_DIGITS))


def parse_year(text: str) -> Optional[int]:
    for match in YEAR_RE.findall(text):
        year = int(normalize_digits(match))
        if year >= MIN_YEAR:
            return year
    return None


def parse_numeric(pattern: re.Pattern, text: str) -> Optional[int]:
    match = pattern.search(text)
    if not match:
        return None
    digits = normalize_digits(match.group(1))
    return int(digits) if digits else None


def extract_text(element: Optional[BeautifulSoup], default: str = "") -> str:
    return element.get_text(" ", strip=True) if element else default


def derive_transmission(text: str) -> Optional[str]:
    text_lower = text.lower()
    if "دنده" in text_lower or "manual" in text_lower:
        return "Manual"
    if "اتومات" in text_lower or "automatic" in text_lower:
        return "Automatic"
    return None


def derive_color(text: str) -> Optional[str]:
    match = re.search(r"(?:رنگ|color)\s*:?\s*([^\s,]+)", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def parse_listing_card(card: BeautifulSoup) -> Optional[SamandListing]:
    link_tag = card.select_one("a[href]")
    url = f"https://bama.ir{link_tag['href']}" if link_tag else BASE_URL

    title = extract_text(card.select_one(".ad-listitem-title")) or extract_text(
        card.select_one("h2")
    )
    facts_block = " ".join(
        extract_text(li) for li in card.select(".ad-listitem-fact, .list-data li")
    )
    desc = extract_text(card.select_one(".ad-listitem-desc")) or extract_text(
        card.select_one(".list-data")
    )
    combined_text = " ".join(filter(None, [title, facts_block, desc, card.get_text(" ", strip=True)]))

    year = parse_year(combined_text)
    if not year or year < MIN_YEAR:
        return None

    price_text = extract_text(card.select_one(".ad-price, .price"))
    mileage_text = extract_text(card.select_one(".ad-kilometer, [data-testid='ad-mileage']"))
    color_text = extract_text(card.select_one(".ad-color")) or derive_color(combined_text)
    transmission = derive_transmission(combined_text)

    price = parse_numeric(PRICE_RE, price_text or combined_text)
    mileage = parse_numeric(MILEAGE_RE, mileage_text or combined_text)

    return SamandListing(
        title=title or "Samand",
        price=price,
        mileage_km=mileage,
        color=color_text or None,
        production_year=year,
        transmission=transmission,
        description=desc or combined_text[:240],
        url=url,
    )


def find_cards(soup: BeautifulSoup) -> Iterable[BeautifulSoup]:
    selectors = [
        "article[class*='ad-listitem']",
        "div[class*='car-list-item']",
        "li[class*='ad-listitem']",
    ]
    for selector in selectors:
        cards = soup.select(selector)
        if cards:
            return cards
    return []


def scrape_page(session: requests.Session, page: int) -> List[SamandListing]:
    params = {"sort": "year-desc", "page": page, "pn": page}
    resp = session.get(BASE_URL, params=params, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = find_cards(soup)
    listings: List[SamandListing] = []
    for card in cards:
        listing = parse_listing_card(card)
        if listing:
            listings.append(listing)
    return listings


def scrape_listings(
    limit: int = 50,
    max_pages: int = 40,
    delay: tuple[float, float] = (1.0, 2.0),
    cookie: Optional[str] = None,
) -> List[SamandListing]:
    session = requests.Session()
    session.headers.update(HEADERS)
    cookie_value = cookie or os.environ.get("BAMA_COOKIE", "")
    if cookie_value:
        session.cookies.update(parse_cookie_string(cookie_value))
    collected: List[SamandListing] = []

    for page in range(1, max_pages + 1):
        try:
            page_listings = scrape_page(session, page)
        except requests.RequestException as exc:
            print(f"[WARN] Failed to fetch page {page}: {exc}")
            continue

        for listing in page_listings:
            collected.append(listing)
            if len(collected) >= limit:
                return collected

        if not page_listings:
            break

        time.sleep(random.uniform(*delay))

    return collected


def parse_cookie_string(cookie_str: str) -> dict[str, str]:
    cookie_dict: dict[str, str] = {}
    for piece in cookie_str.split(";"):
        piece = piece.strip()
        if not piece or "=" not in piece:
            continue
        key, value = piece.split("=", 1)
        cookie_dict[key.strip()] = value.strip()
    return cookie_dict


def write_excel(listings: List[SamandListing], output_path: Path = OUTPUT_PATH) -> None:
    if not listings:
        raise ValueError("No listings scraped; aborting Excel export.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("samand_listings")

    headers = ["id"] + list(asdict(listings[0]).keys())
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row_idx, item in enumerate(listings, start=1):
        values = [row_idx] + list(asdict(item).values())
        for col_idx, value in enumerate(values):
            worksheet.write(row_idx, col_idx, value)

    workbook.close()
    print(f"[INFO] Saved {len(listings)} listings to {output_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Samand listings from bama.ir")
    parser.add_argument("--limit", type=int, default=50, help="Number of listings to collect (default: 50)")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Excel output path")
    parser.add_argument("--max-pages", type=int, default=40, help="Maximum pages to traverse")
    parser.add_argument(
        "--cookie",
        type=str,
        default=os.environ.get("BAMA_COOKIE", ""),
        help="Optional Cookie header value; defaults to BAMA_COOKIE env var if set",
    )
    args = parser.parse_args()

    listings = scrape_listings(limit=args.limit, max_pages=args.max_pages, cookie=args.cookie)
    write_excel(listings, args.output)


if __name__ == "__main__":
    main()

