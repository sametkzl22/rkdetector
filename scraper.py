"""
SahibindenSniper - Scraper Module
Undetected ChromeDriver ile Sahibinden.com'dan veri çekme
"""

import random
import time
import logging

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logger setup with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def fetch_with_browser(target_url: str, max_wait: int = 60) -> str | None:
    """
    Undetected ChromeDriver ile hedef URL'den HTML içerik çeker.
    CAPTCHA çıkarsa kullanıcının çözmesini bekler.
    
    Args:
        target_url: Çekilecek sayfa URL'si
        max_wait: CAPTCHA için maksimum bekleme süresi (saniye)
    
    Returns:
        Başarılıysa HTML içerik, değilse None
    """
    driver = None
    
    try:
        logger.info(f"🌐 Tarayıcı başlatılıyor...")
        
        # Chrome options
        options = uc.ChromeOptions()
        
        # Rastgele pencere boyutu
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        # Headless KAPALI - Sahibinden headless'ı algılıyor
        # options.add_argument("--headless")
        
        # Ek ayarlar
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        
        # Driver başlat
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        logger.info(f"📍 Sayfa yükleniyor: {target_url}")
        driver.get(target_url)
        
        # CAPTCHA kontrolü ve bekleme
        logger.info(f"⏳ Sayfa yükleniyor ve CAPTCHA kontrol ediliyor...")
        
        start_time = time.time()
        content_loaded = False
        
        while time.time() - start_time < max_wait:
            # Sayfa HTML'ini kontrol et
            page_source = driver.page_source
            
            # PerimeterX CAPTCHA var mı kontrol et
            if "px-captcha" in page_source.lower() or "perimeterx" in page_source.lower():
                elapsed = int(time.time() - start_time)
                logger.warning(f"🔒 CAPTCHA tespit edildi! Lütfen tarayıcıda çözün... ({elapsed}s/{max_wait}s)")
                time.sleep(3)
                continue
            
            # Gerçek içerik var mı kontrol et (searchResultsItem)
            if "searchResultsItem" in page_source or "classifiedTitle" in page_source:
                content_loaded = True
                logger.info(f"✓ Gerçek içerik yüklendi!")
                break
            
            # Sahibinden ana sayfa elementleri
            if "sahibinden" in page_source.lower() and len(page_source) > 50000:
                content_loaded = True
                logger.info(f"✓ Sayfa yüklendi ({len(page_source)} karakter)")
                break
            
            time.sleep(2)
        
        if not content_loaded:
            logger.error(f"✗ {max_wait} saniye içinde içerik yüklenemedi.")
            return None
        
        # Ekstra bekleme - sayfanın tam render olması için
        wait_time = random.uniform(3, 5)
        logger.info(f"⏳ {wait_time:.1f} saniye ekstra bekleniyor...")
        time.sleep(wait_time)
        
        # Final HTML al
        html_content = driver.page_source
        
        if html_content and len(html_content) > 10000:
            logger.info(f"✓ Başarılı! {len(html_content)} karakter alındı.")
            return html_content
        else:
            logger.warning(f"⚠ Sayfa içeriği beklenenden kısa: {len(html_content)} karakter")
            return html_content if html_content else None
            
    except Exception as e:
        logger.error(f"✗ Tarayıcı hatası: {e}")
        return None
        
    finally:
        if driver:
            try:
                driver.quit()
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
    html = fetch_with_browser(test_url)
    if html:
        save_html(html)
