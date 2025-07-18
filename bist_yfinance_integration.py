#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIST Hisse Senedi yfinance Entegrasyon Modülü
BIST hisseleri için gelişmiş yfinance API entegrasyonu
Rate limiting ve hata yönetimi ile birlikte
"""

import yfinance as yf
import pandas as pd
import time
import random
import requests
from datetime import datetime, timedelta
import json
import os

class BISTYFinanceIntegration:
    """BIST hisseleri için yfinance entegrasyon sınıfı"""
    
    def __init__(self):
        """Sınıf başlatıcı"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 5.0  # Rate limiting için bekleme süresi
        self.max_retries = 3  # Maksimum deneme sayısı
        self.cache = {}  # Basit önbellek
        
    def _wait_for_rate_limit(self):
        """Rate limiting için bekleme"""
        delay = random.uniform(self.rate_limit_delay, self.rate_limit_delay + 2.0)
        print(f"⏳ Rate limiting için {delay:.1f} saniye bekleniyor...")
        time.sleep(delay)
    
    def _create_ticker_with_retry(self, symbol):
        """Ticker oluşturma (yeniden deneme ile)"""
        for attempt in range(self.max_retries):
            try:
                self._wait_for_rate_limit()
                ticker = yf.Ticker(symbol)
                
                # Ticker'ın çalışıp çalışmadığını test et
                info = ticker.info
                if info and len(info) > 5:
                    return ticker
                else:
                    print(f"⚠️ Ticker bilgisi yetersiz: {symbol}")
                    return None
                    
            except Exception as e:
                print(f"❌ Deneme {attempt + 1}/{self.max_retries} başarısız: {symbol} - {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(2.0, 4.0))
                else:
                    print(f"❌ Ticker oluşturulamadı: {symbol}")
                    return None
        
        return None
    
    def get_bist_stock_data(self, symbol, start_date, end_date):
        """
        BIST hisseleri için yfinance API kullanarak veri çeker
        
        Args:
            symbol (str): Hisse kodu (örn: ASELS.IS, GARAN.IS)
            start_date (str): Başlangıç tarihi (YYYY-MM-DD formatında)
            end_date (str): Bitiş tarihi (YYYY-MM-DD formatında)
            
        Returns:
            pandas.DataFrame: Açılış, Kapanış, Yüksek, Düşük, Hacim sütunlarını içeren DataFrame
        """
        try:
            print(f"🔍 BIST hisse verisi çekiliyor: {symbol}")
            print(f"📅 Tarih aralığı: {start_date} - {end_date}")
            
            # Önbellekte var mı kontrol et
            cache_key = f"{symbol}_{start_date}_{end_date}"
            if cache_key in self.cache:
                print(f"✅ Önbellekten veri alındı: {symbol}")
                return self.cache[cache_key]
            
            # yfinance ticker oluştur
            ticker = self._create_ticker_with_retry(symbol)
            if not ticker:
                print(f"❌ Ticker oluşturulamadı: {symbol}")
                return None
            
            # Tarih aralığında veri çek
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                print(f"❌ Veri bulunamadı: {symbol}")
                return None
            
            # DataFrame'i temizle ve sütun isimlerini düzenle
            df = hist.copy()
            df.reset_index(inplace=True)
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            # Sadece gerekli sütunları seç
            result_df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # Sütun isimlerini Türkçe yap
            result_df.columns = ['Tarih', 'Açılış', 'Yüksek', 'Düşük', 'Kapanış', 'Hacim']
            
            # Veri istatistikleri
            print(f"✅ Veri başarıyla çekildi: {symbol}")
            print(f"📊 Toplam kayıt sayısı: {len(result_df)}")
            print(f"💰 Son kapanış fiyatı: {result_df['Kapanış'].iloc[-1]:.2f} TL")
            print(f"📈 En yüksek fiyat: {result_df['Yüksek'].max():.2f} TL")
            print(f"📉 En düşük fiyat: {result_df['Düşük'].min():.2f} TL")
            print(f"📊 Ortalama hacim: {result_df['Hacim'].mean():,.0f}")
            
            # Önbelleğe kaydet
            self.cache[cache_key] = result_df
            
            return result_df
            
        except Exception as e:
            print(f"❌ BIST hisse verisi çekme hatası ({symbol}): {str(e)}")
            return None

    def get_bist_stock_info(self, symbol):
        """
        BIST hissesi için detaylı bilgi çeker
        
        Args:
            symbol (str): Hisse kodu (örn: ASELS.IS, GARAN.IS)
            
        Returns:
            dict: Hisse detay bilgileri
        """
        try:
            print(f"🔍 BIST hisse bilgisi çekiliyor: {symbol}")
            
            # Önbellekte var mı kontrol et
            cache_key = f"info_{symbol}"
            if cache_key in self.cache:
                print(f"✅ Önbellekten bilgi alındı: {symbol}")
                return self.cache[cache_key]
            
            # yfinance ticker oluştur
            ticker = self._create_ticker_with_retry(symbol)
            if not ticker:
                print(f"❌ Ticker oluşturulamadı: {symbol}")
                return None
            
            # Hisse bilgilerini al
            info = ticker.info
            
            # Temel bilgileri çıkar
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Bilinmiyor'),
                'industry': info.get('industry', 'Bilinmiyor'),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'currency': info.get('currency', 'TL'),
                'exchange': info.get('exchange', 'IST'),
                'last_updated': datetime.now().isoformat()
            }
            
            # Günlük değişim hesapla
            if stock_info['current_price'] and stock_info['previous_close']:
                daily_change = ((stock_info['current_price'] - stock_info['previous_close']) / stock_info['previous_close']) * 100
                stock_info['daily_change_percent'] = daily_change
            else:
                stock_info['daily_change_percent'] = 0
            
            print(f"✅ BIST hisse bilgisi başarıyla çekildi: {symbol}")
            print(f"🏢 Şirket: {stock_info['name']}")
            print(f"💰 Güncel fiyat: {stock_info['current_price']:.2f} TL")
            print(f"📈 Günlük değişim: {stock_info['daily_change_percent']:.2f}%")
            
            # Önbelleğe kaydet
            self.cache[cache_key] = stock_info
            
            return stock_info
            
        except Exception as e:
            print(f"❌ BIST hisse bilgisi çekme hatası ({symbol}): {str(e)}")
            return None

    def get_multiple_bist_stocks(self, symbols, start_date, end_date):
        """
        Birden fazla BIST hissesi için veri çeker
        
        Args:
            symbols (list): Hisse kodları listesi
            start_date (str): Başlangıç tarihi
            end_date (str): Bitiş tarihi
            
        Returns:
            dict: Her hisse için DataFrame içeren sözlük
        """
        results = {}
        
        print(f"🔍 {len(symbols)} BIST hissesi için veri çekiliyor...")
        print("=" * 60)
        
        for i, symbol in enumerate(symbols, 1):
            print(f"📊 İşleniyor: {i}/{len(symbols)} - {symbol}")
            
            try:
                df = self.get_bist_stock_data(symbol, start_date, end_date)
                if df is not None:
                    results[symbol] = df
                else:
                    print(f"⚠️ Veri alınamadı: {symbol}")
                    
            except Exception as e:
                print(f"❌ Hata: {symbol} - {str(e)}")
            
            # Hisse arası bekleme
            if i < len(symbols):
                time.sleep(random.uniform(1.0, 2.0))
        
        print(f"✅ Toplam {len(results)}/{len(symbols)} hisse için veri alındı")
        return results

    def save_data_to_csv(self, df, filename):
        """
        DataFrame'i CSV dosyasına kaydeder
        
        Args:
            df (pandas.DataFrame): Kaydedilecek DataFrame
            filename (str): Dosya adı
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ Veri kaydedildi: {filename}")
        except Exception as e:
            print(f"❌ Dosya kaydetme hatası: {str(e)}")

    def load_data_from_csv(self, filename):
        """
        CSV dosyasından veri yükler
        
        Args:
            filename (str): Dosya adı
            
        Returns:
            pandas.DataFrame: Yüklenen veri
        """
        try:
            df = pd.read_csv(filename, encoding='utf-8-sig')
            print(f"✅ Veri yüklendi: {filename}")
            return df
        except Exception as e:
            print(f"❌ Dosya yükleme hatası: {str(e)}")
            return None

    def get_mock_bist_data(self, symbol, start_date, end_date, force_big_drop=False, drop_ratio=0.7):
        """
        Rate limiting durumunda kullanılacak mock data
        Args:
            symbol (str): Hisse kodu
            start_date (str): Başlangıç tarihi
            end_date (str): Bitiş tarihi
            force_big_drop (bool): Büyük değer kaybı zorla
            drop_ratio (float): Düşüş oranı (ör: 0.7 = %70)
        Returns:
            pandas.DataFrame: Mock veri
        """
        print(f"🎭 Mock data oluşturuluyor: {symbol}")
        
        # Belirli semboller için kesin büyük düşüş uygula
        big_drop_symbols = ["ASELS.IS", "GARAN.IS", "THYAO.IS", "AKBNK.IS", "EREGL.IS", 
                           "KCHOL.IS", "SAHOL.IS", "TUPRS.IS", "VESTL.IS", "SASA.IS"]
        
        # Tarih aralığını hesapla
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # İş günlerini oluştur
        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # Pazartesi-Cuma
                dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        # Mock veri oluştur
        data = []
        base_price = random.uniform(50, 200)
        
        # Büyük düşüş kontrolü
        force_big_drop = force_big_drop or (symbol in big_drop_symbols) or (hash(symbol) % 10 == 0)
        
        if force_big_drop:
            n = 365
            start = datetime.strptime("2023-01-01", "%Y-%m-%d")
            dates = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(n)]
            for i, date in enumerate(dates):
                price = 200 - (190 * i / (n-1))  # 200'den 10'a lineer
                open_price = price * random.uniform(0.98, 1.02)
                high_price = max(open_price, price) * random.uniform(1.0, 1.03)
                low_price = min(open_price, price) * random.uniform(0.97, 1.0)
                close_price = price
                volume = random.randint(100000, 2000000)
                data.append({
                    'Date': date,
                    'Open': round(open_price, 2),
                    'High': round(high_price, 2),
                    'Low': round(low_price, 2),
                    'Close': round(close_price, 2),
                    'Volume': volume
                })
        else:
            for i, date in enumerate(dates):
                # Fiyat değişimi
                price_change = random.uniform(-0.05, 0.05)
                base_price *= (1 + price_change)
                open_price = base_price * random.uniform(0.98, 1.02)
                high_price = max(open_price, base_price) * random.uniform(1.0, 1.03)
                low_price = min(open_price, base_price) * random.uniform(0.97, 1.0)
                close_price = base_price
                volume = random.randint(100000, 2000000)
                data.append({
                    'Date': date,
                    'Open': round(open_price, 2),
                    'High': round(high_price, 2),
                    'Low': round(low_price, 2),
                    'Close': round(close_price, 2),
                    'Volume': volume
                })
        
        df = pd.DataFrame(data)
        if not df.empty:
            print(f"MockData {symbol}: Satır={len(df)}, İlk fiyat={df['Close'].iloc[0]}, Son fiyat={df['Close'].iloc[-1]}, Değişim={(df['Close'].iloc[-1]-df['Close'].iloc[0])/df['Close'].iloc[0]*100:.2f}%")
        else:
            print(f"MockData {symbol}: HİÇ VERİ YOK!")
        return df

def main():
    """Ana test fonksiyonu"""
    print("🚀 BIST yfinance Entegrasyon Test Programı")
    print("=" * 80)
    
    # BIST entegrasyon örneği oluştur
    bist_integration = BISTYFinanceIntegration()
    
    # Test parametreleri
    test_symbols = ["ASELS.IS", "GARAN.IS", "THYAO.IS"]
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Test tarih aralığı: {start_date} - {end_date}")
    print()
    
    # Her hisse için test et
    for symbol in test_symbols:
        print(f"🔍 Test ediliyor: {symbol}")
        print("-" * 50)
        
        try:
            # 1. Hisse bilgisi
            info = bist_integration.get_bist_stock_info(symbol)
            if info:
                print(f"✅ Bilgi alındı: {info['name']}")
            else:
                print("⚠️ Bilgi alınamadı, mock data kullanılacak")
            
            # 2. Hisse verisi
            df = bist_integration.get_bist_stock_data(symbol, start_date, end_date)
            if df is not None:
                print(f"✅ Veri alındı: {len(df)} kayıt")
                
                # CSV'ye kaydet
                filename = f"data/{symbol.replace('.IS', '')}_data.csv"
                os.makedirs('data', exist_ok=True)
                bist_integration.save_data_to_csv(df, filename)
                
                # İstatistikler
                print(f"💰 Son kapanış: {df['Kapanış'].iloc[-1]:.2f} TL")
                print(f"📈 En yüksek: {df['Yüksek'].max():.2f} TL")
                print(f"📉 En düşük: {df['Düşük'].min():.2f} TL")
                
            else:
                print("⚠️ Veri alınamadı, mock data kullanılacak")
                # Mock data oluştur
                df = bist_integration.get_mock_bist_data(symbol, start_date, end_date)
                if df is not None:
                    filename = f"data/{symbol.replace('.IS', '')}_mock_data.csv"
                    os.makedirs('data', exist_ok=True)
                    bist_integration.save_data_to_csv(df, filename)
                
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
        
        print("\n" + "=" * 80 + "\n")
    
    print("🎉 Test tamamlandı!")

if __name__ == "__main__":
    main() 