#!/usr/bin/env python3
"""
Bama.ir scraper for Samand cars (manufactured after 1385).

This script scrapes bama.ir to collect 50 Samand car listings with:
- Price
- Mileage
- Color
- Production year (after 1385)
- Transmission type (manual/automatic)
- Description

Output: Excel file with collected data
"""

import re
import time
import random
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup
import xlsxwriter


# Configuration
BASE_URL = "https://bama.ir/car/samand"
OUTPUT_PATH = Path("data/samand_listings.xlsx")
MIN_YEAR = 1385
TARGET_COUNT = 50

# Headers from curl command
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fa;q=0.7',
    'priority': 'u=0, i',
    'referer': 'https://bama.ir/',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

# Cookies from curl command
COOKIES = {
    'auth.globalUserContextId': '21e8b637-66b1-4bf2-8df5-fcfbba90a266',
    'auth.strategy': 'user',
    'ph_phc_EtFdvBN7bDIyYwxL05EDj95G8GvXQdKdYix4V1CWVJc_posthog': '%7B%22distinct_id%22%3A%2201995dda-4c33-7cd8-b400-318ba23d75b5%22%2C%22%24sesid%22%3A%5B1764360609499%2C%22019acc16-37bf-7c78-b664-17ba096edab1%22%2C1764360599487%5D%7D'
}

# Persian to English digit mapping
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

# Regex patterns
YEAR_PATTERN = re.compile(r'(13\d{2}|14\d{2})')
PRICE_PATTERN = re.compile(r'(\d[\d,\.]*)\s*(?:تومان|ریال|Toman|Rial)?', re.IGNORECASE)
MILEAGE_PATTERN = re.compile(r'(\d[\d,\.]*)\s*(?:کیلومتر|km|kilometer)', re.IGNORECASE)
COLOR_PATTERNS = [
    r'رنگ[:\s]+([^\s,،]+)',
    r'color[:\s]+([^\s,،]+)',
    r'(سفید|مشکی|نقره‌ای|خاکستری|نوک‌مدادی|آبی|قرمز|بژ|قهوه‌ای|زرد|سبز|نارنجی)'
]
TRANSMISSION_PATTERNS = {
    'manual': [r'دنده\s*دستی', r'manual', r'دستی'],
    'automatic': [r'اتومات', r'automatic', r'اتوماتیک']
}


@dataclass
class CarListing:
    """Data class for car listing information."""
    price: Optional[str]
    mileage: Optional[str]
    color: Optional[str]
    production_year: int
    transmission: Optional[str]
    description: str
    url: str


def normalize_persian_digits(text: str) -> str:
    """Convert Persian digits to English digits."""
    if not text:
        return ""
    return text.translate(PERSIAN_DIGITS)


def extract_year(text: str) -> Optional[int]:
    """Extract production year from text."""
    normalized = normalize_persian_digits(text)
    matches = YEAR_PATTERN.findall(normalized)
    for match in matches:
        year = int(match)
        if MIN_YEAR < year < 1500:  # Valid Persian year range
            return year
    return None


def extract_price(text: str) -> Optional[str]:
    """Extract price from text."""
    normalized = normalize_persian_digits(text)
    match = PRICE_PATTERN.search(normalized)
    if match:
        price = match.group(1).replace(',', '').replace('.', '')
        return price if price else "Agreement"
    return "Agreement"


def extract_mileage(text: str) -> Optional[str]:
    """Extract mileage from text."""
    normalized = normalize_persian_digits(text)
    match = MILEAGE_PATTERN.search(normalized)
    if match:
        mileage = match.group(1).replace(',', '').replace('.', '')
        return mileage if mileage else "0"
    return "0"


def extract_color(text: str) -> Optional[str]:
    """Extract color from text."""
    normalized = text
    for pattern in COLOR_PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Unknown"


def extract_transmission(text: str) -> Optional[str]:
    """Extract transmission type from text."""
    text_lower = text.lower()
    for trans_type, patterns in TRANSMISSION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "Automatic" if trans_type == 'automatic' else "Manual"
    return "Unknown"


def parse_listing_card(card: BeautifulSoup) -> Optional[CarListing]:
    """Parse a single car listing card from HTML."""
    # Get all text from the card
    card_text = card.get_text(" ", strip=True)
    normalized_text = normalize_persian_digits(card_text)
    
    # Extract year - must be > 1385
    year = extract_year(normalized_text)
    if not year or year <= MIN_YEAR:
        return None
    
    # Extract price
    price_elem = card.select_one('.ad-price, .price, [class*="price"]')
    price_text = price_elem.get_text(strip=True) if price_elem else card_text
    price = extract_price(price_text)
    
    # Extract mileage
    mileage_elem = card.select_one('.ad-kilometer, .mileage, [class*="mileage"], [class*="kilometer"]')
    mileage_text = mileage_elem.get_text(strip=True) if mileage_elem else card_text
    mileage = extract_mileage(mileage_text)
    
    # Extract color
    color = extract_color(card_text)
    
    # Extract transmission
    transmission = extract_transmission(card_text)
    
    # Extract description/title
    title_elem = card.select_one('h2, .ad-title, [class*="title"]')
    title = title_elem.get_text(strip=True) if title_elem else ""
    desc_elem = card.select_one('.ad-desc, .description, [class*="desc"]')
    desc = desc_elem.get_text(strip=True) if desc_elem else ""
    description = f"{title} - {desc}".strip()[:200] if desc else title[:200]
    if not description:
        description = card_text[:200]
    
    # Extract URL
    link_elem = card.select_one('a[href]')
    if link_elem and link_elem.get('href'):
        href = link_elem['href']
        url = href if href.startswith('http') else f"https://bama.ir{href}"
    else:
        url = BASE_URL
    
    return CarListing(
        price=price,
        mileage=mileage,
        color=color,
        production_year=year,
        transmission=transmission,
        description=description,
        url=url
    )


def find_listing_cards(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """Find all car listing cards in the HTML."""
    # Try multiple selectors as bama.ir structure may vary
    selectors = [
        'article[class*="ad"]',
        'div[class*="ad-list"]',
        'li[class*="ad"]',
        'div[class*="car-item"]',
        'a[href*="/car/detail"]',
        '.bama-ad-holder',
        '[data-testid*="ad"]'
    ]
    
    cards = []
    for selector in selectors:
        found = soup.select(selector)
        if found:
            cards.extend(found)
            break
    
    return cards


def scrape_page(session: requests.Session, page: int) -> List[CarListing]:
    """Scrape a single page of listings."""
    params = {'page': page}
    try:
        response = session.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = find_listing_cards(soup)
    
    listings = []
    for card in cards:
        listing = parse_listing_card(card)
        if listing:
            listings.append(listing)
    
    return listings


def scrape_bama(limit: int = TARGET_COUNT) -> List[CarListing]:
    """Main scraping function."""
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)
    
    collected = []
    page = 1
    max_pages = 50  # Safety limit
    
    print(f"Starting scrape for {limit} Samand cars (Year > {MIN_YEAR})...")
    
    while len(collected) < limit and page <= max_pages:
        print(f"Fetching page {page}... (Collected: {len(collected)}/{limit})")
        
        listings = scrape_page(session, page)
        
        if not listings:
            print(f"No more listings found on page {page}")
            break
        
        # Add unique listings (check by URL)
        existing_urls = {listing.url for listing in collected}
        for listing in listings:
            if listing.url not in existing_urls:
                collected.append(listing)
                if len(collected) >= limit:
                    break
        
        page += 1
        # Random delay to be respectful
        time.sleep(random.uniform(1.0, 2.5))
    
    print(f"Scraping complete! Collected {len(collected)} listings.")
    return collected[:limit]


def save_to_excel(listings: List[CarListing], output_path: Path = OUTPUT_PATH):
    """Save listings to Excel file."""
    if not listings:
        print("No listings to save!")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Samand Listings")
    
    # Headers
    headers = ["Price", "Mileage", "Color", "Production Year", "Transmission", "Description", "URL"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Data
    for row, listing in enumerate(listings, start=1):
        worksheet.write(row, 0, listing.price)
        worksheet.write(row, 1, listing.mileage)
        worksheet.write(row, 2, listing.color)
        worksheet.write(row, 3, listing.production_year)
        worksheet.write(row, 4, listing.transmission)
        worksheet.write(row, 5, listing.description)
        worksheet.write(row, 6, listing.url)
    
    workbook.close()
    print(f"Saved {len(listings)} listings to {output_path.resolve()}")


def main():
    """Main entry point."""
    listings = scrape_bama(limit=TARGET_COUNT)
    if listings:
        save_to_excel(listings)
    else:
        print("No listings found matching the criteria.")


if __name__ == "__main__":
    main()

