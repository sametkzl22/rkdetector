"""
SahibindenSniper - Database Module
SQLite ile ilan verilerini saklama katmanı
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

DB_NAME = "rkdetector.db"


def init_db() -> bool:
    """
    Veritabanını ve listings tablosunu oluşturur.
    
    Returns:
        Başarılıysa True, değilse False
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    price INTEGER,
                    link TEXT,
                    first_seen TEXT,
                    last_seen TEXT
                )
            """)
            conn.commit()
            logger.info(f"✓ Veritabanı hazır: {DB_NAME}")
            return True
    except sqlite3.Error as e:
        logger.error(f"✗ Veritabanı oluşturma hatası: {e}")
        return False


def check_listing(listing_id: str) -> bool:
    """
    İlanın veritabanında olup olmadığını kontrol eder.
    
    Args:
        listing_id: Sahibinden ilan numarası
    
    Returns:
        Varsa True, yoksa False
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM listings WHERE id = ?", (listing_id,))
            result = cursor.fetchone()
            return result is not None
    except sqlite3.Error as e:
        logger.error(f"✗ İlan kontrol hatası [{listing_id}]: {e}")
        return False


def add_listing(data: dict) -> bool:
    """
    Yeni ilanı veritabanına ekler.
    
    Args:
        data: {"id": str, "title": str, "price": int, "link": str}
    
    Returns:
        Başarılıysa True, değilse False
    """
    try:
        now = datetime.now().isoformat()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO listings (id, title, price, link, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["id"],
                data["title"],
                data["price"],
                data["link"],
                now,
                now
            ))
            conn.commit()
            logger.info(f"✓ Yeni ilan eklendi: {data['id']} - {data['title'][:30]}...")
            return True
    except sqlite3.IntegrityError:
        logger.warning(f"⚠ İlan zaten mevcut: {data['id']}")
        return False
    except sqlite3.Error as e:
        logger.error(f"✗ İlan ekleme hatası: {e}")
        return False


def get_listing_price(listing_id: str) -> Optional[int]:
    """
    İlanın kayıtlı son fiyatını döner.
    
    Args:
        listing_id: Sahibinden ilan numarası
    
    Returns:
        Fiyat (int) veya bulunamazsa None
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price FROM listings WHERE id = ?", (listing_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"✗ Fiyat sorgulama hatası [{listing_id}]: {e}")
        return None


def update_listing(listing_id: str, new_price: int) -> bool:
    """
    İlanın fiyatını ve last_seen tarihini günceller.
    
    Args:
        listing_id: Sahibinden ilan numarası
        new_price: Yeni fiyat
    
    Returns:
        Başarılıysa True, değilse False
    """
    try:
        now = datetime.now().isoformat()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE listings 
                SET price = ?, last_seen = ?
                WHERE id = ?
            """, (new_price, now, listing_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"✓ İlan güncellendi: {listing_id} → {new_price} TL")
                return True
            else:
                logger.warning(f"⚠ İlan bulunamadı: {listing_id}")
                return False
    except sqlite3.Error as e:
        logger.error(f"✗ İlan güncelleme hatası [{listing_id}]: {e}")
        return False


if __name__ == "__main__":
    # Test
    init_db()
    
    test_data = {
        "id": "TEST123",
        "title": "Test iPhone 15 Pro Max",
        "price": 75000,
        "link": "https://www.sahibinden.com/ilan/TEST123"
    }
    
    add_listing(test_data)
    print(f"İlan var mı? {check_listing('TEST123')}")
    print(f"Fiyat: {get_listing_price('TEST123')} TL")
    update_listing("TEST123", 72000)
    print(f"Yeni fiyat: {get_listing_price('TEST123')} TL")
