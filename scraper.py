"""
SahibindenSniper - Scraper Module
ZenRows API ile Sahibinden.com'dan veri çekme
"""

import os
import time
import logging
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
ZENROWS_BASE_URL = "https://api.zenrows.com/v1/"

# Logger setup with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def fetch_with_zenrows(target_url: str, max_retries: int = 3, retry_delay: int = 5) -> str | None:
    """
    ZenRows API ile hedef URL'den HTML içerik çeker.
    
    Args:
        target_url: Çekilecek sayfa URL'si
        max_retries: Maksimum deneme sayısı (default: 3)
        retry_delay: Denemeler arası bekleme süresi (saniye, default: 5)
    
    Returns:
        Başarılıysa HTML içerik, değilse None
    """
    if not ZENROWS_API_KEY:
        logger.error("ZENROWS_API_KEY bulunamadı! .env dosyasını kontrol edin.")
        return None
    
    params = {
        "url": target_url,
        "apikey": ZENROWS_API_KEY,
        "premium_proxy": "true",
        "js_render": "true"
    }
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Deneme {attempt}/{max_retries} → {target_url}")
            
            response = requests.get(ZENROWS_BASE_URL, params=params, timeout=60)
            
            if response.status_code == 200:
                logger.info(f"✓ Başarılı! {len(response.text)} karakter alındı.")
                return response.text
            else:
                logger.warning(f"✗ HTTP {response.status_code}: {response.text[:200]}")
        
        except requests.exceptions.Timeout:
            logger.error(f"✗ Timeout! İstek zaman aşımına uğradı.")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ İstek hatası: {e}")
        
        if attempt < max_retries:
            logger.info(f"↻ {retry_delay} saniye bekleniyor...")
            time.sleep(retry_delay)
    
    logger.error(f"✗ {max_retries} deneme sonrası başarısız.")
    return None


def save_html(content: str, filename: str = "sahibinden_raw.html") -> bool:
    """
    HTML içeriği dosyaya kaydeder.
    
    Args:
        content: Kaydedilecek HTML içerik
        filename: Dosya adı (default: sahibinden_raw.html)
    
    Returns:
        Başarılıysa True, değilse False
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"✓ HTML kaydedildi → {filename}")
        return True
    except IOError as e:
        logger.error(f"✗ Dosya yazma hatası: {e}")
        return False


if __name__ == "__main__":
    # Test için standalone çalıştırma
    test_url = "https://www.sahibinden.com/cep-telefonu"
    html = fetch_with_zenrows(test_url)
    if html:
        save_html(html)
