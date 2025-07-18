#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIST Hisse Sembolleri Test Modülü
Doğru BIST hisse sembol formatını bulmak için test eder
"""

import yfinance as yf
import time
import random

def test_bist_symbols():
    """Farklı BIST sembol formatlarını test eder"""
    print("🔍 BIST Hisse Sembolleri Test Ediliyor...")
    print("=" * 60)
    
    # Test edilecek farklı sembol formatları
    test_formats = [
        "ASELS.IS",      # Standart format
        "ASELS",         # Sadece kod
        "ASELS.TI",      # TI formatı
        "ASELS.IST",     # IST formatı
        "ASELS.TR",      # TR formatı
        "ASELS.TO",      # TO formatı
        "ASELSAN.IS",    # Tam isim
        "ASELSAN",       # Tam isim sadece
        "ASELSAN.TI",    # Tam isim TI
    ]
    
    for symbol in test_formats:
        print(f"🔍 Test ediliyor: {symbol}")
        print("-" * 40)
        
        try:
            # Rate limiting için bekleme
            time.sleep(random.uniform(2.0, 3.0))
            
            # Ticker oluştur
            ticker = yf.Ticker(symbol)
            
            # Basit bilgi almayı dene
            info = ticker.info
            
            if info and len(info) > 5:
                print(f"✅ Başarılı: {symbol}")
                print(f"🏢 Şirket: {info.get('longName', 'Bilinmiyor')}")
                print(f"💰 Güncel fiyat: {info.get('currentPrice', 'Bilinmiyor')}")
                print(f"💱 Para birimi: {info.get('currency', 'Bilinmiyor')}")
                print(f"🏛️ Borsa: {info.get('exchange', 'Bilinmiyor')}")
                
                # Son 5 günlük veri almayı dene
                hist = ticker.history(period="5d")
                if not hist.empty:
                    print(f"📊 Son kapanış: {hist['Close'].iloc[-1]:.2f}")
                    print(f"📈 Veri satır sayısı: {len(hist)}")
                else:
                    print("❌ Geçmiş veri alınamadı")
                    
            else:
                print(f"❌ Başarısız: {symbol} - Yetersiz bilgi")
                
        except Exception as e:
            print(f"❌ Hata: {symbol} - {str(e)}")
        
        print("\n" + "=" * 60 + "\n")

def test_popular_bist_stocks():
    """Popüler BIST hisselerini test eder"""
    print("🔍 Popüler BIST Hisseleri Test Ediliyor...")
    print("=" * 60)
    
    # Popüler BIST hisseleri
    popular_stocks = [
        "GARAN.IS",      # Garanti Bankası
        "THYAO.IS",      # Türk Hava Yolları
        "AKBNK.IS",      # Akbank
        "EREGL.IS",      # Ereğli Demir ve Çelik
        "KCHOL.IS",      # Koç Holding
        "SAHOL.IS",      # Sabancı Holding
        "SISE.IS",       # Şişe Cam
        "TUPRS.IS",      # Tüpraş
        "BIMAS.IS",      # BİM
        "ASELS.IS",      # Aselsan
    ]
    
    successful_stocks = []
    
    for symbol in popular_stocks:
        print(f"🔍 Test ediliyor: {symbol}")
        print("-" * 40)
        
        try:
            # Rate limiting için bekleme
            time.sleep(random.uniform(3.0, 4.0))
            
            # Ticker oluştur
            ticker = yf.Ticker(symbol)
            
            # Basit bilgi almayı dene
            info = ticker.info
            
            if info and len(info) > 5:
                print(f"✅ Başarılı: {symbol}")
                print(f"🏢 Şirket: {info.get('longName', 'Bilinmiyor')}")
                print(f"💰 Güncel fiyat: {info.get('currentPrice', 'Bilinmiyor')}")
                successful_stocks.append(symbol)
            else:
                print(f"❌ Başarısız: {symbol}")
                
        except Exception as e:
            print(f"❌ Hata: {symbol} - {str(e)}")
        
        print()
    
    print("📊 Test Sonuçları:")
    print(f"✅ Başarılı: {len(successful_stocks)}/{len(popular_stocks)}")
    print(f"📋 Başarılı hisseler: {', '.join(successful_stocks)}")

def test_yfinance_connection():
    """yfinance bağlantısını test eder"""
    print("🔍 yfinance Bağlantı Testi...")
    print("=" * 60)
    
    try:
        # Basit bir ABD hissesi ile test et
        print("🔍 ABD hissesi test ediliyor: AAPL")
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and len(info) > 5:
            print("✅ yfinance bağlantısı başarılı")
            print(f"🏢 Test hissesi: {info.get('longName', 'Apple Inc.')}")
            print(f"💰 Güncel fiyat: {info.get('currentPrice', 'Bilinmiyor')}")
        else:
            print("❌ yfinance bağlantısı başarısız")
            
    except Exception as e:
        print(f"❌ yfinance bağlantı hatası: {str(e)}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 BIST Hisse Sembolleri Test Programı")
    print("=" * 80)
    
    # 1. yfinance bağlantı testi
    test_yfinance_connection()
    print("\n" + "=" * 80 + "\n")
    
    # 2. Sembol formatları testi
    test_bist_symbols()
    
    # 3. Popüler hisseler testi
    test_popular_bist_stocks()
    
    print("\n🎉 Test tamamlandı!")

if __name__ == "__main__":
    main() 