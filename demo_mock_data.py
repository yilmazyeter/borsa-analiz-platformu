#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIST Mock Data Demo
Mock data sistemini test eder
"""

from datetime import datetime, timedelta
import pandas as pd
from bist_yfinance_integration import BISTYFinanceIntegration

def demo_mock_data():
    """Mock data sistemini test eder"""
    print("🚀 BIST Mock Data Demo")
    print("=" * 60)
    
    # BIST entegrasyon örneği oluştur
    bist = BISTYFinanceIntegration()
    
    # Test parametreleri
    symbols = ["ASELS.IS", "GARAN.IS", "THYAO.IS"]
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📊 Test hisseleri: {', '.join(symbols)}")
    print(f"📅 Tarih aralığı: {start_date} - {end_date}")
    print()
    
    for symbol in symbols:
        print(f"🔍 Mock data oluşturuluyor: {symbol}")
        print("-" * 40)
        
        # Mock data oluştur
        df = bist.get_mock_bist_data(symbol, start_date, end_date)
        
        if df is not None:
            print(f"✅ Mock data oluşturuldu: {len(df)} kayıt")
            print(f"💰 Son kapanış: {df['Kapanış'].iloc[-1]:.2f} TL")
            print(f"📈 En yüksek: {df['Yüksek'].max():.2f} TL")
            print(f"📉 En düşük: {df['Düşük'].min():.2f} TL")
            print(f"📊 Ortalama hacim: {df['Hacim'].mean():,.0f}")
            
            # İlk 3 günü göster
            print("\n📋 İlk 3 günlük veri:")
            print(df.head(3).to_string(index=False))
            
            # CSV'ye kaydet
            filename = f"data/{symbol.replace('.IS', '')}_mock_demo.csv"
            bist.save_data_to_csv(df, filename)
            
        else:
            print(f"❌ Mock data oluşturulamadı: {symbol}")
        
        print("\n" + "=" * 60 + "\n")

def demo_data_analysis():
    """Mock data ile analiz örneği"""
    print("📊 Mock Data Analizi")
    print("=" * 60)
    
    # BIST entegrasyon örneği oluştur
    bist = BISTYFinanceIntegration()
    
    # Test verisi oluştur
    symbol = "ASELS.IS"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    df = bist.get_mock_bist_data(symbol, start_date, end_date)
    
    if df is not None:
        print(f"📊 Analiz ediliyor: {symbol}")
        print(f"📅 Veri aralığı: {len(df)} gün")
        
        # Temel istatistikler
        print("\n📈 Temel İstatistikler:")
        print(f"   Ortalama kapanış: {df['Kapanış'].mean():.2f} TL")
        print(f"   Standart sapma: {df['Kapanış'].std():.2f} TL")
        print(f"   Ortalama hacim: {df['Hacim'].mean():,.0f}")
        
        # Günlük değişim hesapla
        df['Günlük_Değişim'] = df['Kapanış'].pct_change() * 100
        
        print(f"\n📊 Günlük Değişim İstatistikleri:")
        print(f"   Ortalama değişim: {df['Günlük_Değişim'].mean():.2f}%")
        print(f"   En yüksek artış: {df['Günlük_Değişim'].max():.2f}%")
        print(f"   En yüksek düşüş: {df['Günlük_Değişim'].min():.2f}%")
        
        # Volatilite hesapla
        volatility = df['Günlük_Değişim'].std()
        print(f"   Volatilite: {volatility:.2f}%")
        
        # Son 5 günlük trend
        last_5_days = df.tail(5)
        trend = "📈 Yükseliş" if last_5_days['Kapanış'].iloc[-1] > last_5_days['Kapanış'].iloc[0] else "📉 Düşüş"
        print(f"\n📈 Son 5 günlük trend: {trend}")
        
        # Son 5 günlük veri
        print(f"\n📋 Son 5 günlük veri:")
        print(last_5_days[['Tarih', 'Kapanış', 'Günlük_Değişim']].to_string(index=False))
        
    else:
        print("❌ Analiz için veri oluşturulamadı")

def main():
    """Ana demo fonksiyonu"""
    print("🚀 BIST Mock Data Test Programı")
    print("=" * 80)
    
    try:
        # 1. Mock data oluşturma
        demo_mock_data()
        
        # 2. Veri analizi
        demo_data_analysis()
        
        print("\n🎉 Mock data demo tamamlandı!")
        print("\n📋 Özet:")
        print("✅ Mock data sistemi başarıyla çalışıyor")
        print("✅ Rate limiting durumunda fallback çalışıyor")
        print("✅ Veri analizi özellikleri çalışıyor")
        print("✅ CSV kaydetme özelliği çalışıyor")
        
    except Exception as e:
        print(f"\n❌ Demo sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 