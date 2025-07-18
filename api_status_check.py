#!/usr/bin/env python3
"""
API Durumu Kontrol Scripti
Tüm API'lerin durumunu kontrol eder ve raporlar
"""

import requests
import time
from datetime import datetime

# API Anahtarları
ALPHA_VANTAGE_API_KEY = 'GJ34QCRSULNFYKUL'
TWELVE_DATA_API_KEY = '0972e9caa03b454fad5eadca558d6eb8'
IEX_CLOUD_API_KEY = 'pk_test_1234567890abcdef'
MARKETSTACK_API_KEY = 'aead57355e25b386aa1ad49d1d448807'
FMP_API_KEY = 'c8v62RyLXJAfjT4IsMspZV9XsBbZiB0j'

def test_alpha_vantage():
    """Alpha Vantage API test"""
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey={ALPHA_VANTAGE_API_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            return 'invalid_key', f"Geçersiz anahtar: {data['Error Message']}"
        elif 'Note' in data:
            return 'limit_reached', f"Limit aşıldı: {data['Note']}"
        elif 'Time Series (Daily)' in data:
            return 'active', "API çalışıyor"
        else:
            return 'unknown', "Bilinmeyen yanıt"
    except Exception as e:
        return 'error', f"Bağlantı hatası: {str(e)}"

def test_twelve_data():
    """Twelve Data API test"""
    try:
        url = f'https://api.twelvedata.com/time_series?symbol=AAPL&interval=1day&outputsize=1&apikey={TWELVE_DATA_API_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'status' in data and data['status'] == 'error':
            return 'invalid_key', f"Geçersiz anahtar: {data.get('message', 'Bilinmeyen hata')}"
        elif 'values' in data and len(data['values']) > 0:
            return 'active', "API çalışıyor"
        else:
            return 'unknown', "Bilinmeyen yanıt"
    except Exception as e:
        return 'error', f"Bağlantı hatası: {str(e)}"

def test_iex_cloud():
    """IEX Cloud API test"""
    try:
        url = f'https://cloud.iexapis.com/stable/stock/AAPL/quote?token={IEX_CLOUD_API_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'error' in data:
            return 'invalid_key', f"Geçersiz anahtar: {data['error']}"
        elif 'latestPrice' in data:
            return 'active', "API çalışıyor"
        else:
            return 'unknown', "Bilinmeyen yanıt"
    except Exception as e:
        return 'error', f"Bağlantı hatası: {str(e)}"

def test_marketstack():
    """MarketStack API test"""
    try:
        url = f'http://api.marketstack.com/v1/eod?access_key={MARKETSTACK_API_KEY}&symbols=AAPL&limit=1'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'error' in data:
            return 'invalid_key', f"Geçersiz anahtar: {data['error']}"
        elif 'data' in data and data['data']:
            return 'active', "API çalışıyor"
        else:
            return 'unknown', "Bilinmeyen yanıt"
    except Exception as e:
        return 'error', f"Bağlantı hatası: {str(e)}"

def test_fmp():
    """Financial Modeling Prep API test"""
    try:
        url = f'https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={FMP_API_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            return 'active', "API çalışıyor"
        elif isinstance(data, dict) and 'Error Message' in data:
            return 'invalid_key', f"Geçersiz anahtar: {data['Error Message']}"
        else:
            return 'unknown', "Bilinmeyen yanıt"
    except Exception as e:
        return 'error', f"Bağlantı hatası: {str(e)}"

def test_yahoo_finance():
    """Yahoo Finance API test (yfinance)"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and len(info) > 5:
            return 'active', "API çalışıyor"
        else:
            return 'rate_limited', "Rate limiting veya veri bulunamadı"
    except Exception as e:
        return 'error', f"Bağlantı hatası: {str(e)}"

def main():
    """Ana test fonksiyonu"""
    print("🔍 API Durumu Kontrol Ediliyor...")
    print("=" * 60)
    print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test edilecek API'ler
    apis = [
        ("Alpha Vantage", test_alpha_vantage),
        ("Twelve Data", test_twelve_data),
        ("IEX Cloud", test_iex_cloud),
        ("MarketStack", test_marketstack),
        ("Financial Modeling Prep", test_fmp),
        ("Yahoo Finance", test_yahoo_finance)
    ]
    
    results = []
    
    for api_name, test_func in apis:
        print(f"\n🔍 {api_name} test ediliyor...")
        status, message = test_func()
        results.append((api_name, status, message))
        
        # Status emoji
        status_emoji = {
            'active': '✅',
            'invalid_key': '❌',
            'limit_reached': '🚫',
            'rate_limited': '⏳',
            'error': '⚠️',
            'unknown': '❓'
        }.get(status, '❓')
        
        print(f"{status_emoji} {api_name}: {status} - {message}")
        
        # API'ler arası bekleme
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("📊 ÖZET RAPOR")
    print("=" * 60)
    
    # Özet istatistikler
    active_count = sum(1 for _, status, _ in results if status == 'active')
    error_count = sum(1 for _, status, _ in results if status in ['invalid_key', 'limit_reached', 'rate_limited', 'error'])
    
    print(f"✅ Çalışan API'ler: {active_count}")
    print(f"❌ Sorunlu API'ler: {error_count}")
    print(f"📊 Toplam API: {len(results)}")
    
    print("\n🔧 ÖNERİLER:")
    if error_count > 0:
        print("1. Geçersiz API anahtarlarını güncelleyin")
        print("2. Rate limiting için bekleme sürelerini artırın")
        print("3. Ücretli API planlarına geçmeyi düşünün")
        print("4. Mock data kullanımını artırın")
    else:
        print("🎉 Tüm API'ler çalışıyor!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 