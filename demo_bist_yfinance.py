#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIST Hisse Senedi yfinance Entegrasyon Demo
Kullanım örnekleri ve pratik uygulamalar
"""

from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from bist_yfinance_integration import BISTYFinanceIntegration

def demo_basic_usage():
    """Temel kullanım örneği"""
    print("🚀 BIST yfinance Entegrasyon - Temel Kullanım")
    print("=" * 60)
    
    # BIST entegrasyon örneği oluştur
    bist = BISTYFinanceIntegration()
    
    # Test parametreleri
    symbol = "ASELS.IS"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📊 Hisse: {symbol}")
    print(f"📅 Tarih aralığı: {start_date} - {end_date}")
    print()
    
    # 1. Hisse bilgisi al
    print("🔍 Hisse bilgisi alınıyor...")
    info = bist.get_bist_stock_info(symbol)
    
    if info:
        print("✅ Hisse bilgisi:")
        print(f"   🏢 Şirket: {info['name']}")
        print(f"   💰 Güncel fiyat: {info['current_price']:.2f} TL")
        print(f"   📈 Günlük değişim: {info['daily_change_percent']:.2f}%")
        print(f"   🏭 Sektör: {info['sector']}")
        print(f"   📊 P/E Oranı: {info['pe_ratio']:.2f}")
    else:
        print("⚠️ Hisse bilgisi alınamadı")
    
    print()
    
    # 2. Hisse verisi al
    print("📈 Hisse verisi alınıyor...")
    df = bist.get_bist_stock_data(symbol, start_date, end_date)
    
    if df is not None:
        print("✅ Hisse verisi:")
        print(f"   📊 Toplam kayıt: {len(df)}")
        print(f"   💰 Son kapanış: {df['Kapanış'].iloc[-1]:.2f} TL")
        print(f"   📈 En yüksek: {df['Yüksek'].max():.2f} TL")
        print(f"   📉 En düşük: {df['Düşük'].min():.2f} TL")
        
        # İlk 5 günü göster
        print("\n📋 İlk 5 günlük veri:")
        print(df.head().to_string(index=False))
        
        return df
    else:
        print("❌ Hisse verisi alınamadı")
        return None

def demo_multiple_stocks():
    """Birden fazla hisse örneği"""
    print("\n🚀 Çoklu Hisse Verisi")
    print("=" * 60)
    
    # BIST entegrasyon örneği oluştur
    bist = BISTYFinanceIntegration()
    
    # Test hisseleri
    symbols = ["ASELS.IS", "GARAN.IS", "THYAO.IS"]
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"📊 Hisseler: {', '.join(symbols)}")
    print(f"📅 Tarih aralığı: {start_date} - {end_date}")
    print()
    
    # Çoklu hisse verisi al
    results = bist.get_multiple_bist_stocks(symbols, start_date, end_date)
    
    if results:
        print("✅ Alınan veriler:")
        for symbol, df in results.items():
            if df is not None:
                print(f"   📊 {symbol}: {len(df)} kayıt, Son fiyat: {df['Kapanış'].iloc[-1]:.2f} TL")
        
        return results
    else:
        print("❌ Veri alınamadı")
        return None

def demo_data_analysis(df):
    """Veri analizi örneği"""
    if df is None or df.empty:
        print("❌ Analiz için veri yok")
        return
    
    print("\n📊 Veri Analizi")
    print("=" * 60)
    
    # Temel istatistikler
    print("📈 Temel İstatistikler:")
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
    
    return df

def demo_visualization(df):
    """Görselleştirme örneği"""
    if df is None or df.empty:
        print("❌ Görselleştirme için veri yok")
        return
    
    print("\n📊 Görselleştirme")
    print("=" * 60)
    
    try:
        # Matplotlib ayarları
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('BIST Hisse Senedi Analizi', fontsize=16, fontweight='bold')
        
        # 1. Fiyat grafiği
        axes[0, 0].plot(df['Tarih'], df['Kapanış'], marker='o', linewidth=2, markersize=4)
        axes[0, 0].set_title('Kapanış Fiyatları')
        axes[0, 0].set_xlabel('Tarih')
        axes[0, 0].set_ylabel('Fiyat (TL)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Hacim grafiği
        axes[0, 1].bar(df['Tarih'], df['Hacim'], alpha=0.7, color='skyblue')
        axes[0, 1].set_title('İşlem Hacmi')
        axes[0, 1].set_xlabel('Tarih')
        axes[0, 1].set_ylabel('Hacim')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. OHLC grafiği (son 10 gün)
        last_10 = df.tail(10)
        axes[1, 0].plot(last_10['Tarih'], last_10['Yüksek'], label='Yüksek', marker='^', color='green')
        axes[1, 0].plot(last_10['Tarih'], last_10['Düşük'], label='Düşük', marker='v', color='red')
        axes[1, 0].plot(last_10['Tarih'], last_10['Kapanış'], label='Kapanış', marker='o', color='blue')
        axes[1, 0].set_title('OHLC Grafiği (Son 10 Gün)')
        axes[1, 0].set_xlabel('Tarih')
        axes[1, 0].set_ylabel('Fiyat (TL)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Günlük değişim histogramı
        df['Günlük_Değişim'] = df['Kapanış'].pct_change() * 100
        axes[1, 1].hist(df['Günlük_Değişim'].dropna(), bins=10, alpha=0.7, color='orange', edgecolor='black')
        axes[1, 1].set_title('Günlük Değişim Dağılımı')
        axes[1, 1].set_xlabel('Günlük Değişim (%)')
        axes[1, 1].set_ylabel('Frekans')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Grafiği kaydet
        filename = f"data/bist_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Grafik kaydedildi: {filename}")
        
        # Grafiği göster
        plt.show()
        
    except Exception as e:
        print(f"❌ Görselleştirme hatası: {str(e)}")

def demo_csv_operations():
    """CSV işlemleri örneği"""
    print("\n💾 CSV İşlemleri")
    print("=" * 60)
    
    # BIST entegrasyon örneği oluştur
    bist = BISTYFinanceIntegration()
    
    # Test verisi oluştur
    symbol = "ASELS.IS"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Veri al
    df = bist.get_bist_stock_data(symbol, start_date, end_date)
    
    if df is not None:
        # CSV'ye kaydet
        filename = f"data/{symbol.replace('.IS', '')}_demo.csv"
        bist.save_data_to_csv(df, filename)
        
        # CSV'den yükle
        loaded_df = bist.load_data_from_csv(filename)
        
        if loaded_df is not None:
            print("✅ CSV işlemleri başarılı")
            print(f"   📊 Yüklenen veri: {len(loaded_df)} kayıt")
            print(f"   📋 Sütunlar: {list(loaded_df.columns)}")
        else:
            print("❌ CSV yükleme hatası")
    else:
        print("❌ Veri alınamadı")

def main():
    """Ana demo fonksiyonu"""
    print("🚀 BIST Hisse Senedi yfinance Entegrasyon Demo")
    print("=" * 80)
    
    try:
        # 1. Temel kullanım
        df = demo_basic_usage()
        
        # 2. Çoklu hisse
        multi_results = demo_multiple_stocks()
        
        # 3. Veri analizi
        if df is not None:
            df = demo_data_analysis(df)
            
            # 4. Görselleştirme
            demo_visualization(df)
        
        # 5. CSV işlemleri
        demo_csv_operations()
        
        print("\n🎉 Demo tamamlandı!")
        print("\n📋 Özet:")
        print("✅ yfinance entegrasyonu başarıyla eklendi")
        print("✅ Rate limiting yönetimi uygulandı")
        print("✅ Mock data fallback sistemi eklendi")
        print("✅ CSV kaydetme/yükleme özelliği eklendi")
        print("✅ Veri analizi ve görselleştirme örnekleri eklendi")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Demo sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    main() 