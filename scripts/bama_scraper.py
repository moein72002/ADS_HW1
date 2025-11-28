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
import xlsxwriter

# --- Configuration ---
API_URL = "https://bama.ir/cad/api/search"
OUTPUT_PATH = Path("data/samand_listings.xlsx")
MIN_YEAR = 1385
TARGET_COUNT = 50

# Headers for API requests (from curl command)
API_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fa;q=0.7',
    'priority': 'u=1, i',
    'referer': 'https://bama.ir/car/samand',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'x-user-context': '21e8b637-66b1-4bf2-8df5-fcfbba90a266'
}

# Cookie from the curl command (broken down)
COOKIES = {
    "auth.globalUserContextId": "21e8b637-66b1-4bf2-8df5-fcfbba90a266",
    "auth.strategy": "user",
    "ph_phc_EtFdvBN7bDIyYwxL05EDj95G8GvXQdKdYix4V1CWVJc_posthog": "%7B%22distinct_id%22%3A%2201995dda-4c33-7cd8-b400-318ba23d75b5%22%2C%22%24sesid%22%3A%5B1764360627577%2C%22019acc16-37bf-7c78-b664-17ba096edab1%22%2C1764360599487%5D%7D"
}

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

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
    """Convert Persian digits to English and normalize text."""
    if not text:
        return ""
    return text.strip().translate(PERSIAN_DIGITS)

def parse_year(year_str: str) -> Optional[int]:
    """Parse Persian year string to integer."""
    if not year_str:
        return None
    normalized = normalize_text(year_str)
    try:
        year = int(normalized)
        if MIN_YEAR < year < 1500:  # Valid Persian year range
            return year
    except ValueError:
        pass
    return None

def extract_transmission(transmission_str: str) -> str:
    """Extract transmission type from Persian text."""
    if not transmission_str:
        return "Unknown"
    t = transmission_str.lower()
    if "دنده" in t or "manual" in t:
        return "Manual"
    if "اتومات" in t or "automatic" in t:
        return "Automatic"
    return "Unknown"

def parse_mileage(mileage_str: str) -> str:
    """Extract mileage number from string like '66,000 km'."""
    if not mileage_str:
        return "0"
    # Remove 'km' and commas, keep only digits
    normalized = normalize_text(mileage_str.replace("km", "").replace("کیلومتر", ""))
    return normalized if normalized else "0"

def parse_price(price_data: Dict) -> str:
    """Extract price from price object."""
    if not price_data:
        return "Agreement"
    price_str = price_data.get("price", "")
    if price_str:
        # Remove commas
        return price_str.replace(",", "")
    return "Agreement"

def parse_api_listing(ad_data: Dict) -> Optional[CarListing]:
    """
    Parse a single car listing from API JSON response.
    """
    detail = ad_data.get("detail", {})
    price_data = ad_data.get("price", {})
    
    # Extract year
    year_str = detail.get("year", "")
    year = parse_year(year_str)
    if not year or year <= MIN_YEAR:
        return None  # Skip if too old or year not found
    
    # Extract price
    price = parse_price(price_data)
    
    # Extract mileage
    mileage_str = detail.get("mileage", "")
    mileage = parse_mileage(mileage_str)
    
    # Extract transmission
    transmission_str = detail.get("transmission", "")
    transmission = extract_transmission(transmission_str)
    
    # Extract color
    color = detail.get("color", "") or detail.get("body_color", "") or "Unknown"
    if not color or color == "":
        color = "Unknown"
    
    # Extract description
    description = detail.get("description", "") or detail.get("title", "") or ""
    if not description:
        subtitle = detail.get("subtitle", "")
        title = detail.get("title", "")
        description = f"{title} - {subtitle}".strip()
    
    # Extract URL
    url_path = detail.get("url", "")
    url = f"https://bama.ir{url_path}" if url_path else ""
    
    return CarListing(
        price=price,
        mileage=mileage,
        color=color,
        production_year=year,
        transmission=transmission,
        description=description[:200],  # Limit description length
        url=url
    )

def scrape_bama(limit: int = 50):
    """Scrape Samand cars from bama.ir using API endpoint."""
    collected_cars: List[CarListing] = []
    page_index = 1
    
    session = requests.Session()
    session.headers.update(API_HEADERS)
    session.cookies.update(COOKIES)

    print(f"Starting scrape for {limit} Samand cars (Year > {MIN_YEAR})...")

    while len(collected_cars) < limit:
        print(f"Fetching page {page_index}... (Collected: {len(collected_cars)}/{limit})")
        try:
            # Use API endpoint with pageIndex parameter
            params = {
                "vehicle": "samand",
                "pageIndex": page_index
            }
            resp = session.get(API_URL, params=params, timeout=30)
            
            if resp.status_code != 200:
                print(f"Error fetching page {page_index}: {resp.status_code}")
                break
            
            # Parse JSON response
            data = resp.json()
            
            if not data.get("status", False):
                print(f"API returned error: {data.get('errors', [])}")
                break
            
            # Get metadata
            metadata = data.get("metadata", {})
            total_pages = metadata.get("total_pages", 0)
            total_count = metadata.get("total_count", 0)
            
            print(f"  Total listings: {total_count}, Total pages: {total_pages}")
            
            # Get ads from response
            ads_data = data.get("data", {}).get("ads", [])
            
            if not ads_data:
                print("No listings found on this page. Ending scrape.")
                break

            print(f"  Found {len(ads_data)} listings on page {page_index}")

            page_new_count = 0
            for ad in ads_data:
                car = parse_api_listing(ad)
                if car:
                    # Avoid duplicates (check by URL)
                    if not any(c.url == car.url for c in collected_cars):
                        collected_cars.append(car)
                        page_new_count += 1
                        if len(collected_cars) >= limit:
                            break
            
            print(f"  Added {page_new_count} new cars from page {page_index} (Total: {len(collected_cars)})")
            
            # Check if there are more pages
            if page_index >= total_pages or not metadata.get("has_next", False):
                print(f"  Reached last page ({total_pages})")
                break
            
            page_index += 1
            time.sleep(random.uniform(0.8, 1.5))  # Be respectful with API

        except requests.RequestException as e:
            print(f"Network error on page {page_index}: {e}")
            break
        except ValueError as e:
            print(f"JSON parsing error on page {page_index}: {e}")
            break
        except Exception as e:
            print(f"Exception on page {page_index}: {e}")
            import traceback
            traceback.print_exc()
            break

    return collected_cars

def save_to_excel(cars: List[CarListing], path: Path):
    """Save listings to Excel file with file locking handling."""
    if not cars:
        print("No listings to save!")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # If file exists and is locked, try with timestamp
    if path.exists():
        try:
            # Try to remove existing file if possible
            path.unlink()
        except (PermissionError, OSError):
            # If can't remove, use timestamped filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = path.parent / f"samand_listings_{timestamp}.xlsx"
            print(f"File locked, using alternative name: {path.name}")
    
    try:
        workbook = xlsxwriter.Workbook(str(path))
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
        print(f"Saved {len(cars)} cars to {path.resolve()}")
    except PermissionError as e:
        # Try with a different filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alt_path = path.parent / f"samand_listings_{timestamp}.xlsx"
        print(f"Permission denied, trying alternative filename: {alt_path.name}")
        return save_to_excel(cars, alt_path)
    except Exception as e:
        print(f"Error saving Excel file: {e}")
        raise

if __name__ == "__main__":
    cars = scrape_bama(limit=TARGET_COUNT)
    if cars:
        save_to_excel(cars, OUTPUT_PATH)
    else:
        print("No cars found matching criteria.")

