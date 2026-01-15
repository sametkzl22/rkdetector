"""
Cloudflare Bypass Module
Based on: https://github.com/sarperavci/CloudflareBypassForScraping
"""

import time
import logging

logger = logging.getLogger(__name__)


class CloudflareBypasser:
    """
    Cloudflare Turnstile CAPTCHA otomatik bypass sınıfı.
    DrissionPage ChromiumPage instance'ı ile çalışır.
    """
    
    def __init__(self, driver, max_retries: int = 10, log: bool = True):
        """
        Args:
            driver: DrissionPage ChromiumPage instance
            max_retries: Maksimum deneme sayısı (-1 = sonsuz)
            log: Loglama aktif mi
        """
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def search_recursively_shadow_root_with_iframe(self, ele):
        """Shadow root içinde iframe arar"""
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self, ele):
        """Shadow root içinde Cloudflare input arar"""
        if ele.shadow_root:
            if ele.shadow_root.ele("tag:input"):
                return ele.shadow_root.ele("tag:input")
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None

    def locate_cf_button(self):
        """Cloudflare doğrulama butonunu bulur"""
        button = None
        eles = self.driver.eles("tag:input")
        
        for ele in eles:
            if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
                if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                    button = ele.parent().shadow_root.child()("tag:body").shadow_root("tag:input")
                    break

        if button:
            return button
        else:
            self.log_message("Basit arama başarısız. Recursive arama yapılıyor...")
            ele = self.driver.ele("tag:body")
            iframe = self.search_recursively_shadow_root_with_iframe(ele)
            if iframe:
                button = self.search_recursively_shadow_root_with_cf_input(iframe("tag:body"))
            else:
                self.log_message("Iframe bulunamadı.")
            return button

    def log_message(self, message: str):
        """Mesaj logla"""
        if self.log:
            logger.info(f"🔐 CF Bypass: {message}")

    def click_verification_button(self):
        """Doğrulama butonuna tıklar"""
        try:
            button = self.locate_cf_button()
            if button:
                self.log_message("Doğrulama butonu bulundu. Tıklanıyor...")
                button.click()
            else:
                self.log_message("Doğrulama butonu bulunamadı.")
        except Exception as e:
            self.log_message(f"Buton tıklama hatası: {e}")

    def is_bypassed(self) -> bool:
        """Bypass başarılı mı kontrol eder"""
        try:
            title = self.driver.title.lower()
            return "just a moment" not in title
        except Exception as e:
            self.log_message(f"Sayfa başlığı kontrol hatası: {e}")
            return False

    def bypass(self) -> bool:
        """
        Cloudflare korumasını bypass etmeye çalışır.
        
        Returns:
            Başarılıysa True, değilse False
        """
        try_count = 0

        while not self.is_bypassed():
            if 0 < self.max_retries + 1 <= try_count:
                self.log_message("Maksimum deneme aşıldı. Bypass başarısız.")
                return False

            self.log_message(f"Deneme {try_count + 1}: Doğrulama sayfası tespit edildi...")
            self.click_verification_button()

            try_count += 1
            time.sleep(2)

        if self.is_bypassed():
            self.log_message("✓ Bypass başarılı!")
            return True
        else:
            self.log_message("✗ Bypass başarısız.")
            return False
