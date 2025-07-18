#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIST Hisse Senedi yfinance API Test Modülü
BIST hisseleri için yfinance entegrasyonunu test eder
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Proje dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.stock_scraper import StockScraper

def test_bist_stock_data():
    """BIST hisse verisi çekme fonksiyonunu test eder"""
    print("🧪 BIST Hisse Verisi Test Başlıyor...")
    print("=" * 60)
    
    # StockScraper örneği oluştur
    scraper = StockScraper()
    
    # Test parametreleri
    test_symbols = [
        "ASELS.IS",  # Aselsan
        "GARAN.IS",  # Garanti Bankası
        "THYAO.IS",  # Türk Hava Yolları
        "AKBNK.IS",  # Akbank
        "EREGL.IS"   # Ereğli Demir ve Çelik
    ]
    
    # Tarih aralığı (son 30 gün)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Test tarih aralığı: {start_date} - {end_date}")
    print()
    
    for symbol in test_symbols:
        print(f"🔍 Test ediliyor: {symbol}")
        print("-" * 40)
        
        try:
            # Hisse verisi çek
            df = scraper.get_bist_stock_data(symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                print(f"✅ Başarılı: {symbol}")
                print(f"📊 Veri satır sayısı: {len(df)}")
                print(f"💰 Son kapanış: {df['Kapanış'].iloc[-1]:.2f} TL")
                print(f"📈 En yüksek: {df['Yüksek'].max():.2f} TL")
                print(f"📉 En düşük: {df['Düşük'].min():.2f} TL")
                print(f"📊 Ortalama hacim: {df['Hacim'].mean():,.0f}")
                
                # İlk 5 satırı göster
                print("\n📋 İlk 5 günlük veri:")
                print(df.head().to_string(index=False))
                
            else:
                print(f"❌ Başarısız: {symbol} - Veri alınamadı")
                
        except Exception as e:
            print(f"❌ Hata: {symbol} - {str(e)}")
        
        print("\n" + "=" * 60 + "\n")

def test_bist_stock_info():
    """BIST hisse bilgisi çekme fonksiyonunu test eder"""
    print("🧪 BIST Hisse Bilgisi Test Başlıyor...")
    print("=" * 60)
    
    # StockScraper örneği oluştur
    scraper = StockScraper()
    
    # Test sembolleri
    test_symbols = [
        "ASELS.IS",  # Aselsan
        "GARAN.IS",  # Garanti Bankası
        "THYAO.IS"   # Türk Hava Yolları
    ]
    
    for symbol in test_symbols:
        print(f"🔍 Test ediliyor: {symbol}")
        print("-" * 40)
        
        try:
            # Hisse bilgisi çek
            info = scraper.get_bist_stock_info(symbol)
            
            if info:
                print(f"✅ Başarılı: {symbol}")
                print(f"🏢 Şirket: {info.get('name', 'Bilinmiyor')}")
                print(f"💰 Güncel fiyat: {info.get('current_price', 0):.2f} TL")
                print(f"📈 Günlük değişim: {info.get('daily_change_percent', 0):.2f}%")
                print(f"📊 Piyasa değeri: {info.get('market_cap', 0):,.0f} TL")
                print(f"🏭 Sektör: {info.get('sector', 'Bilinmiyor')}")
                print(f"🏭 Endüstri: {info.get('industry', 'Bilinmiyor')}")
                print(f"📊 P/E Oranı: {info.get('pe_ratio', 0):.2f}")
                print(f"📊 P/B Oranı: {info.get('pb_ratio', 0):.2f}")
                print(f"💵 Temettü verimi: {info.get('dividend_yield', 0):.2f}%")
                
            else:
                print(f"❌ Başarısız: {symbol} - Bilgi alınamadı")
                
        except Exception as e:
            print(f"❌ Hata: {symbol} - {str(e)}")
        
        print("\n" + "=" * 60 + "\n")

def test_dataframe_operations():
    """DataFrame işlemlerini test eder"""
    print("🧪 DataFrame İşlemleri Test Başlıyor...")
    print("=" * 60)
    
    # StockScraper örneği oluştur
    scraper = StockScraper()
    
    # Test sembolü
    symbol = "ASELS.IS"
    
    # Son 7 günlük veri
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"🔍 Test ediliyor: {symbol} ({start_date} - {end_date})")
    print("-" * 40)
    
    try:
        # Veri çek
        df = scraper.get_bist_stock_data(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            print("✅ Veri başarıyla çekildi")
            print(f"📊 DataFrame boyutu: {df.shape}")
            print(f"📋 Sütunlar: {list(df.columns)}")
            
            # Veri tiplerini kontrol et
            print("\n📋 Veri tipleri:")
            print(df.dtypes)
            
            # İstatistiksel özet
            print("\n📊 Sayısal sütunların istatistikleri:")
            numeric_cols = ['Açılış', 'Yüksek', 'Düşük', 'Kapanış', 'Hacim']
            print(df[numeric_cols].describe())
            
            # Günlük değişim hesapla
            df['Günlük_Değişim'] = df['Kapanış'].pct_change() * 100
            
            print("\n📈 Günlük değişim istatistikleri:")
            print(f"Ortalama günlük değişim: {df['Günlük_Değişim'].mean():.2f}%")
            print(f"En yüksek artış: {df['Günlük_Değişim'].max():.2f}%")
            print(f"En yüksek düşüş: {df['Günlük_Değişim'].min():.2f}%")
            
            # Son 3 günlük veri
            print("\n📋 Son 3 günlük veri:")
            print(df.tail(3).to_string(index=False))
            
        else:
            print(f"❌ Veri alınamadı: {symbol}")
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 BIST Hisse Senedi yfinance API Test Programı")
    print("=" * 80)
    
    # API durumunu kontrol et
    scraper = StockScraper()
    scraper.check_api_status()
    print()
    
    # Testleri çalıştır
    try:
        # 1. Hisse verisi testi
        test_bist_stock_data()
        
        # 2. Hisse bilgisi testi
        test_bist_stock_info()
        
        # 3. DataFrame işlemleri testi
        test_dataframe_operations()
        
        print("🎉 Tüm testler tamamlandı!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 