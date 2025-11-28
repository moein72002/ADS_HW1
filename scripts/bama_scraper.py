#!/usr/bin/env python3
"""
Scrape Samand car listings from bama.ir matching the HW1 bonus requirements.
This script is located in scripts/ and outputs to data/samand_listings.xlsx.

Extracts:
- Price
- Mileage
- Color
- Production year (>1385)
- Transmission type (manual/automatic)
- Description

Usage:
    python scripts/bama_scraper.py
"""

import os
import re
import time
import random
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup
import xlsxwriter

# --- Configuration ---
BASE_URL = "https://bama.ir/car/samand"
OUTPUT_PATH = Path("data/samand_listings.xlsx")
MIN_YEAR = 1385
TARGET_COUNT = 50

# Headers from the user's curl command
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fa;q=0.7',
    'cache-control': 'no-cache',
    # 'cookie': ... # We will handle cookies separately or add them here if static
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

# Cookie from the curl command (broken down)
COOKIES = {
    "auth.globalUserContextId": "21e8b637-66b1-4bf2-8df5-fcfbba90a266",
    "auth.strategy": "user",
    "ph_phc_EtFdvBN7bDIyYwxL05EDj95G8GvXQdKdYix4V1CWVJc_posthog": "%7B%22distinct_id%22%3A%2201995dda-4c33-7cd8-b400-318ba23d75b5%22%2C%22%24sesid%22%3A%5B1764360609499%2C%22019acc16-37bf-7c78-b664-17ba096edab1%22%2C1764360599487%5D%7D"
}

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
YEAR_RE = re.compile(r"(13\d{2}|14\d{2})")

@dataclass
class CarListing:
    price: Optional[str]
    mileage: Optional[str]
    color: Optional[str]
    production_year: int
    transmission: Optional[str]
    description: str
    url: str

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return text.strip().translate(PERSIAN_DIGITS)

def parse_year(text: str) -> Optional[int]:
    # Look for 4 digit years starting with 13 or 14
    matches = YEAR_RE.findall(normalize_text(text))
    for m in matches:
        y = int(m)
        if 1300 < y < 1500:
            return y
    return None

def extract_transmission(text: str) -> str:
    t = text.lower()
    if "دنده" in t or "manual" in t:
        return "Manual"
    if "اتومات" in t or "automatic" in t:
        return "Automatic"
    return "Unknown"

def parse_card(card: BeautifulSoup) -> Optional[CarListing]:
    """
    Parses a single car listing card from bama.ir.
    """
    # Title/Description often contains year, model, etc.
    title_tag = card.select_one(".bama-ad-holder h2") or card.select_one("h2")
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    # Bama usually has list of details (year, mileage, transmission, etc.)
    # The structure often changes, so we look for specific text patterns or classes.
    
    details_text = card.get_text(" ", strip=True)
    norm_details = normalize_text(details_text)

    # 1. Year
    year = parse_year(norm_details)
    if not year or year <= MIN_YEAR:
        return None # Skip if too old or year not found

    # 2. Price
    # Usually in a specific class or recognizable by 'تومان'
    price_tag = card.select_one(".bama-ad-price") or card.select_one(".price")
    if price_tag:
        price = price_tag.get_text(strip=True)
    else:
        # Regex for price
        p_match = re.search(r"(\d[\d,]*)\s*(?:تومان|ریال)", norm_details)
        price = p_match.group(1) if p_match else "Agreement"

    # 3. Mileage
    mileage_tag = card.select_one(".bama-ad-mileage") or card.select_one(".mileage") 
    if mileage_tag:
        mileage = mileage_tag.get_text(strip=True)
    else:
        # Updated regex to handle 'km' as well
        m_match = re.search(r"(\d[\d,]*)\s*(?:کیلومتر|km)", norm_details, re.IGNORECASE)
        mileage = m_match.group(1) if m_match else "0"

    # 4. Transmission
    transmission = extract_transmission(norm_details)

    # 5. Color
    # Often not explicitly labeled in card, sometimes in description or title
    # We can try to find common colors
    colors = ["سفید", "مشکی", "نقره‌ای", "خاکستری", "نوک‌مدادی", "آبی", "قرمز", "بژ", "قهوه‌ای"]
    color = "Unknown"
    for c in colors:
        if c in norm_details:
            color = c
            break
            
    # 6. Description/Title
    description = title + " - " + details_text[:100] + "..."

    # Link
    link_tag = card.select_one("a")
    url = ""
    if link_tag and link_tag.get("href"):
        url = "https://bama.ir" + link_tag["href"]

    return CarListing(
        price=price,
        mileage=mileage,
        color=color,
        production_year=year,
        transmission=transmission,
        description=description,
        url=url
    )

def scrape_bama(limit: int = 50):
    collected_cars: List[CarListing] = []
    page = 1
    
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    print(f"Starting scrape for {limit} Samand cars (Year > {MIN_YEAR})...")

    while len(collected_cars) < limit:
        print(f"Fetching page {page}... (Collected: {len(collected_cars)}/{limit})")
        try:
            # Bama uses page query param
            resp = session.get(f"{BASE_URL}?page={page}", timeout=15)
            if resp.status_code != 200:
                print(f"Error fetching page {page}: {resp.status_code}")
                break
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Try multiple strategies to find cards
            # 1. Specific containers
            cards = soup.select("div.bama-ad-holder, a.bama-ad, .ad-list-item, li.car-list-item")
            
            # 2. Links that look like car details
            if not cards:
                 cards = soup.select("a[href*='/car/detail']")

            if not cards:
                print("No listings found on this page. Ending scrape.")
                break

            print(f"Found {len(cards)} potential cards on page {page}")

            for card in cards:
                car = parse_card(card)
                if car:
                    # Avoid duplicates if possible (url check)
                    if not any(c.url == car.url for c in collected_cars):
                        collected_cars.append(car)
                        if len(collected_cars) >= limit:
                            break
            
            page += 1
            time.sleep(random.uniform(0.5, 1.5)) # Slightly faster

        except Exception as e:
            print(f"Exception on page {page}: {e}")
            break

    return collected_cars

def save_to_excel(cars: List[CarListing], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet("Samand Listings")

    headers = ["Price", "Mileage", "Color", "Production Year", "Transmission", "Description", "URL"]
    for col, h in enumerate(headers):
        worksheet.write(0, col, h)

    for row, car in enumerate(cars, start=1):
        worksheet.write(row, 0, car.price)
        worksheet.write(row, 1, car.mileage)
        worksheet.write(row, 2, car.color)
        worksheet.write(row, 3, car.production_year)
        worksheet.write(row, 4, car.transmission)
        worksheet.write(row, 5, car.description)
        worksheet.write(row, 6, car.url)

    workbook.close()
    print(f"Saved {len(cars)} cars to {path}")

if __name__ == "__main__":
    cars = scrape_bama(limit=TARGET_COUNT)
    if cars:
        save_to_excel(cars, OUTPUT_PATH)
    else:
        print("No cars found matching criteria.")

