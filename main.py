"""
SahibindenSniper - Main Entry Point
Sonsuz döngüde çalışan "Sniper Bot"
"""

import time
import signal
import sys
import logging

from scraper import fetch_listing_html, save_html, logger

# Hedef URL
TARGET_URL = "https://www.sahibinden.com/cep-telefonu"

# Döngü aralığı (saniye) - 10 dakika
LOOP_INTERVAL = 600

# Graceful shutdown flag
running = True


def signal_handler(signum, frame):
    """Ctrl+C ile temiz çıkış"""
    global running
    logger.info("⚠ Kapatma sinyali alındı. Döngü sonlandırılıyor...")
    running = False


def main():
    """Ana döngü"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("🚀 SahibindenSniper başlatıldı!")
    logger.info(f"📍 Hedef: {TARGET_URL}")
    logger.info(f"⏱  Aralık: {LOOP_INTERVAL // 60} dakika")
    logger.info("=" * 60)
    
    cycle = 0
    
    while running:
        cycle += 1
        logger.info(f"\n{'─' * 40}")
        logger.info(f"📡 Döngü #{cycle} başlıyor...")
        
        # DrissionPage ile veri çek
        html_content = fetch_listing_html(TARGET_URL)
        
        if html_content:
            # HTML'i kaydet
            save_html(html_content)
            logger.info(f"✅ Döngü #{cycle} tamamlandı.")
        else:
            logger.warning(f"⚠ Döngü #{cycle} başarısız - veri alınamadı.")
        
        if running:
            logger.info(f"💤 {LOOP_INTERVAL // 60} dakika bekleniyor...")
            
            # Bekleme süresini küçük parçalara böl (graceful shutdown için)
            for _ in range(LOOP_INTERVAL):
                if not running:
                    break
                time.sleep(1)
    
    logger.info("=" * 60)
    logger.info("👋 SahibindenSniper kapatıldı.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
