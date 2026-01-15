"""
SahibindenSniper - Scraper Module
DrissionPage + CloudflareBypasser ile Sahibinden.com'dan veri çekme
"""

import time
import logging

from DrissionPage import ChromiumPage, ChromiumOptions
from cf_bypass import CloudflareBypasser

# Logger setup with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def fetch_listing_html(url: str, max_retries: int = 10) -> str | None:
    """
    DrissionPage + CloudflareBypasser ile hedef URL'den HTML içerik çeker.
    
    Args:
        url: Çekilecek sayfa URL'si
        max_retries: Cloudflare bypass için maksimum deneme
    
    Returns:
        Başarılıysa HTML içerik, değilse None
    """
    page = None
    
    try:
        logger.info(f"🌐 DrissionPage tarayıcısı başlatılıyor...")
        
        # Chrome options
        options = ChromiumOptions()
        options.set_argument('--no-first-run')
        options.set_argument('--no-default-browser-check')
        options.set_argument('--disable-infobars')
        
        # Tarayıcıyı başlat
        page = ChromiumPage(options)
        
        logger.info(f"📍 Sayfa yükleniyor: {url}")
        page.get(url)
        
        # CloudflareBypasser ile korumayı aş
        logger.info(f"🔐 Cloudflare bypass başlatılıyor...")
        bypasser = CloudflareBypasser(driver=page, max_retries=max_retries, log=True)
        bypass_success = bypasser.bypass()
        
        if not bypass_success:
            logger.error("✗ Cloudflare bypass başarısız.")
            return None
        
        # Ekstra bekleme - sayfanın tam render olması için
        time.sleep(3)
        
        # HTML al
        html_content = page.html
        
        if html_content and len(html_content) > 10000:
            logger.info(f"✓ Başarılı! {len(html_content)} karakter alındı.")
            return html_content
        else:
            logger.warning(f"⚠ Sayfa içeriği beklenenden kısa: {len(html_content) if html_content else 0} karakter")
            return html_content if html_content else None
            
    except Exception as e:
        logger.error(f"✗ Scraper hatası: {e}")
        return None
        
    finally:
        if page:
            try:
                page.quit()
                logger.info("🔒 Tarayıcı kapatıldı.")
            except Exception:
                pass


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
    html = fetch_listing_html(test_url)
    if html:
        save_html(html)
