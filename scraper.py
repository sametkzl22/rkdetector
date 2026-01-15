"""
SahibindenSniper - Scraper Module
DrissionPage ile Sahibinden.com'dan veri çekme (Cloudflare Bypass)
"""

import time
import logging

from DrissionPage import ChromiumPage, ChromiumOptions

# Logger setup with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def fetch_listing_html(url: str, max_wait: int = 60) -> str | None:
    """
    DrissionPage ile hedef URL'den HTML içerik çeker.
    CAPTCHA çıkarsa kullanıcının çözmesini bekler.
    
    Args:
        url: Çekilecek sayfa URL'si
        max_wait: CAPTCHA için maksimum bekleme süresi (saniye)
    
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
        
        # Headless KAPALI - Cloudflare görsel doğrulama isteyebilir
        # options.headless(True)
        
        # Tarayıcıyı başlat
        page = ChromiumPage(options)
        
        logger.info(f"📍 Sayfa yükleniyor: {url}")
        page.get(url)
        
        # CAPTCHA kontrolü ve bekleme
        logger.info(f"⏳ Sayfa yükleniyor ve CAPTCHA kontrol ediliyor...")
        
        start_time = time.time()
        content_loaded = False
        
        while time.time() - start_time < max_wait:
            html_content = page.html
            
            # PerimeterX / Cloudflare CAPTCHA kontrolü
            if "px-captcha" in html_content.lower() or "perimeterx" in html_content.lower() or "turnstile" in html_content.lower():
                elapsed = int(time.time() - start_time)
                logger.warning(f"🔒 CAPTCHA tespit edildi! Lütfen tarayıcıda çözün... ({elapsed}s/{max_wait}s)")
                time.sleep(3)
                continue
            
            # Gerçek içerik kontrolü
            if "searchResultsItem" in html_content or "classifiedTitle" in html_content:
                content_loaded = True
                logger.info(f"✓ Gerçek içerik yüklendi!")
                break
            
            # Sahibinden ana içerik kontrolü
            if len(html_content) > 50000:
                content_loaded = True
                logger.info(f"✓ Sayfa yüklendi ({len(html_content)} karakter)")
                break
            
            time.sleep(2)
        
        if not content_loaded:
            logger.error(f"✗ {max_wait} saniye içinde içerik yüklenemedi.")
            return None
        
        # Ekstra bekleme
        time.sleep(3)
        
        # Final HTML al
        html_content = page.html
        
        if html_content and len(html_content) > 10000:
            logger.info(f"✓ Başarılı! {len(html_content)} karakter alındı.")
            return html_content
        else:
            logger.warning(f"⚠ Sayfa içeriği beklenenden kısa: {len(html_content)} karakter")
            return html_content if html_content else None
            
    except Exception as e:
        logger.error(f"✗ DrissionPage hatası: {e}")
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
