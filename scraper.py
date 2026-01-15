"""
SahibindenSniper - Scraper Module
DrissionPage + Persistent Profile ile Sahibinden.com'dan veri çekme
"""

import os
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

# Kalıcı profil dizini
PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profile")


def is_captcha_page(page) -> bool:
    """PerimeterX CAPTCHA sayfası mı kontrol eder"""
    try:
        title = page.title.lower() if page.title else ""
        html = page.html.lower() if page.html else ""
        
        captcha_indicators = [
            "olağan dışı erişim",
            "unusual access",
            "px-captcha",
            "perimeterx",
            "just a moment"
        ]
        
        for indicator in captcha_indicators:
            if indicator in title or indicator in html:
                return True
        return False
    except Exception:
        return False


def fetch_listing_html(url: str) -> str | None:
    """
    DrissionPage + Persistent Profile ile hedef URL'den HTML içerik çeker.
    CAPTCHA çıkarsa kullanıcının manuel çözmesini bekler.
    
    Args:
        url: Çekilecek sayfa URL'si
    
    Returns:
        Başarılıysa HTML içerik, değilse None
    """
    page = None
    
    try:
        logger.info(f"🌐 DrissionPage tarayıcısı başlatılıyor...")
        logger.info(f"📁 Profil dizini: {PROFILE_PATH}")
        
        # Chrome options with persistent profile
        options = ChromiumOptions()
        options.set_user_data_path(PROFILE_PATH)
        options.set_argument('--no-first-run')
        options.set_argument('--no-default-browser-check')
        options.set_argument('--disable-infobars')
        
        # Tarayıcıyı başlat
        page = ChromiumPage(options)
        
        logger.info(f"📍 Sayfa yükleniyor: {url}")
        page.get(url)
        
        # Sayfa yüklenene kadar kısa bekleme
        time.sleep(3)
        
        # CAPTCHA kontrolü
        if is_captcha_page(page):
            logger.warning("=" * 60)
            logger.warning("⚠️  PerimeterX CAPTCHA Tespit Edildi!")
            logger.warning("=" * 60)
            logger.warning("👆 Lütfen açılan tarayıcı penceresinde CAPTCHA'yı manuel olarak çözün.")
            logger.warning("✅ Çözdükten sonra buraya gelip Enter'a basın...")
            logger.warning("=" * 60)
            
            # Kullanıcının Enter'a basmasını bekle
            input("\n>>> CAPTCHA'yı çözdükten sonra Enter'a basın: ")
            
            logger.info("🔄 Sayfa yeniden kontrol ediliyor...")
            time.sleep(2)
            
            # Hâlâ CAPTCHA varsa hata ver
            if is_captcha_page(page):
                logger.error("✗ CAPTCHA hâlâ mevcut. Lütfen tekrar deneyin.")
                return None
        
        # Ekstra bekleme - sayfanın tam render olması için
        time.sleep(3)
        
        # HTML al
        html_content = page.html
        
        if html_content and len(html_content) > 50000:
            logger.info(f"✓ Başarılı! {len(html_content)} karakter alındı.")
            return html_content
        elif html_content and len(html_content) > 10000:
            logger.warning(f"⚠ Sayfa alındı ama beklenenden kısa: {len(html_content)} karakter")
            return html_content
        else:
            logger.error(f"✗ Sayfa içeriği çok kısa: {len(html_content) if html_content else 0} karakter")
            return None
            
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
