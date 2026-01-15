"""
SahibindenSniper - Parser Module
HTML içerikten ürün verilerini çıkarma
"""

import re
import logging
from bs4 import BeautifulSoup

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.sahibinden.com"


def clean_price(price_text: str) -> int:
    """
    Fiyat stringini temizleyip integer'a çevirir.
    Örnek: "10.500 TL" -> 10500
    
    Args:
        price_text: Ham fiyat metni
    
    Returns:
        Temizlenmiş fiyat (int)
    """
    # Sadece rakamları al
    digits = re.sub(r"[^\d]", "", price_text)
    return int(digits) if digits else 0


def parse_listings(html_content: str) -> list[dict]:
    """
    Sahibinden HTML'inden ürün listesini parse eder.
    
    Args:
        html_content: Ham HTML içerik
    
    Returns:
        Ürün listesi: [{"id": str, "title": str, "price": int, "link": str}, ...]
    """
    listings = []
    
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        rows = soup.find_all("tr", class_="searchResultsItem")
        
        logger.info(f"📋 {len(rows)} ilan satırı bulundu.")
        
        for row in rows:
            try:
                # ID
                listing_id = row.get("data-id")
                if not listing_id:
                    continue
                
                # Başlık ve Link
                title_elem = row.find("a", class_="classifiedTitle")
                if not title_elem:
                    logger.warning(f"⚠ Başlık bulunamadı: {listing_id}")
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")
                
                # Link'e domain ekle
                if link and not link.startswith("http"):
                    link = BASE_URL + link
                
                # Fiyat
                price_elem = row.find("td", class_="searchResultsPriceValue")
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = clean_price(price_text)
                else:
                    price = 0
                    logger.warning(f"⚠ Fiyat bulunamadı: {listing_id}")
                
                listings.append({
                    "id": listing_id,
                    "title": title,
                    "price": price,
                    "link": link
                })
                
            except Exception as e:
                logger.error(f"✗ Satır parse hatası: {e}")
                continue
        
        logger.info(f"✓ {len(listings)} ilan başarıyla parse edildi.")
        
    except Exception as e:
        logger.error(f"✗ HTML parse hatası: {e}")
    
    return listings


if __name__ == "__main__":
    # Test: sahibinden_raw.html dosyasını oku ve parse et
    try:
        with open("sahibinden_raw.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        logger.info("📂 sahibinden_raw.html okundu.")
        
        listings = parse_listings(html)
        
        print("\n" + "=" * 60)
        print(f"📊 TOPLAM: {len(listings)} ilan")
        print("=" * 60)
        
        for i, item in enumerate(listings[:10], 1):  # İlk 10 ilan
            print(f"\n[{i}] ID: {item['id']}")
            print(f"    Başlık: {item['title'][:50]}...")
            print(f"    Fiyat: {item['price']:,} TL")
            print(f"    Link: {item['link']}")
        
        if len(listings) > 10:
            print(f"\n... ve {len(listings) - 10} ilan daha.")
            
    except FileNotFoundError:
        logger.error("✗ sahibinden_raw.html bulunamadı. Önce scraper.py veya main.py çalıştırın.")
