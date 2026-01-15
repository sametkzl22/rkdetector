"""
SahibindenSniper - Parser Module
HTML içerikten ürün verilerini çıkarma (İskelet)
"""

from bs4 import BeautifulSoup


def parse_listings(html_content: str) -> list[dict]:
    """
    Sahibinden HTML'inden ürün listesini parse eder.
    
    Args:
        html_content: Ham HTML içerik
    
    Returns:
        Ürün listesi: [{"title": str, "price": str, "link": str}, ...]
    
    TODO: İleride implementasyon eklenecek
    """
    # İskelet - ileride doldurulacak
    pass


def extract_product_details(listing_element) -> dict:
    """
    Tek bir ürün elementinden detayları çıkarır.
    
    Args:
        listing_element: BeautifulSoup element
    
    Returns:
        {"title": str, "price": str, "link": str}
    
    TODO: İleride implementasyon eklenecek
    """
    # İskelet - ileride doldurulacak
    pass


if __name__ == "__main__":
    # Test için standalone çalıştırma
    try:
        with open("sahibinden_raw.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        listings = parse_listings(html)
        print(f"Parse edilecek içerik hazır. Fonksiyon henüz implement edilmedi.")
    except FileNotFoundError:
        print("sahibinden_raw.html bulunamadı. Önce scraper.py çalıştırın.")
