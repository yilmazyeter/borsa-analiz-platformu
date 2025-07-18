#!/usr/bin/env python3
"""
BIST Hisse API Çözümleri
Türk hisseleri için alternatif veri kaynakları
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json

def get_bist_data_from_investing():
    """Investing.com'dan BIST verisi çeker"""
    try:
        # Investing.com BIST-100 sayfası
        url = "https://tr.investing.com/indices/bist-100"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # BIST-100 tablosunu bul
        table = soup.find('table', {'id': 'cr1'})
        if table:
            rows = table.find_all('tr')[1:]  # İlk satır başlık
            stocks = []
            
            for row in rows[:10]:  # İlk 10 hisse
                cols = row.find_all('td')
                if len(cols) >= 3:
                    symbol = cols[0].text.strip()
                    price = cols[1].text.strip()
                    change = cols[2].text.strip()
                    
                    stocks.append({
                        'symbol': symbol,
                        'price': price,
                        'change': change
                    })
            
            return stocks
        return None
        
    except Exception as e:
        print(f"Investing.com hatası: {str(e)}")
        return None

def get_bist_data_from_bigpara():
    """Bigpara'dan BIST verisi çeker"""
    try:
        # Bigpara BIST-100 sayfası
        url = "https://bigpara.hurriyet.com.tr/borsa/canli-borsa/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # BIST-100 tablosunu bul
        table = soup.find('table', {'class': 'market-data-table'})
        if table:
            rows = table.find_all('tr')[1:]  # İlk satır başlık
            stocks = []
            
            for row in rows[:10]:  # İlk 10 hisse
                cols = row.find_all('td')
                if len(cols) >= 3:
                    symbol = cols[0].text.strip()
                    price = cols[1].text.strip()
                    change = cols[2].text.strip()
                    
                    stocks.append({
                        'symbol': symbol,
                        'price': price,
                        'change': change
                    })
            
            return stocks
        return None
        
    except Exception as e:
        print(f"Bigpara hatası: {str(e)}")
        return None

def get_bist_data_from_foreks():
    """Foreks'ten BIST verisi çeker"""
    try:
        # Foreks BIST-100 API
        url = "https://www.foreks.com/api/v1/stocks/bist100"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        if 'data' in data:
            stocks = []
            for item in data['data'][:10]:  # İlk 10 hisse
                stocks.append({
                    'symbol': item.get('symbol', ''),
                    'price': item.get('price', ''),
                    'change': item.get('change', '')
                })
            return stocks
        return None
        
    except Exception as e:
        print(f"Foreks hatası: {str(e)}")
        return None

def create_mock_bist_data():
    """BIST hisseleri için gerçekçi mock data oluşturur"""
    bist_stocks = [
        'THYAO', 'GARAN', 'AKBNK', 'YAPI', 'KRDMD', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL',
        'BIMAS', 'AKSA', 'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO'
    ]
    
    import random
    from datetime import datetime, timedelta
    
    mock_data = []
    
    for symbol in bist_stocks:
        # Gerçekçi fiyat aralıkları
        base_price = random.uniform(10, 200)
        current_price = base_price * random.uniform(0.8, 1.2)
        
        # Son 30 günlük veri
        historical_data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            price = base_price * random.uniform(0.7, 1.3)
            
            historical_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Open': price * random.uniform(0.98, 1.02),
                'High': price * random.uniform(1.0, 1.05),
                'Low': price * random.uniform(0.95, 1.0),
                'Close': price,
                'Volume': random.randint(1000000, 10000000)
            })
        
        # Son veriyi güncel fiyat yap
        historical_data[-1]['Close'] = current_price
        
        # Değişim hesapla
        prev_price = historical_data[-2]['Close'] if len(historical_data) > 1 else current_price
        daily_change = ((current_price - prev_price) / prev_price) * 100
        
        stock_data = {
            'symbol': symbol,
            'current_price': current_price,
            'previous_price': prev_price,
            'daily_change': daily_change,
            'yearly_change': random.uniform(-50, 100),
            'current_volume': historical_data[-1]['Volume'],
            'avg_volume': sum([d['Volume'] for d in historical_data[-20:]]) / 20,
            'volume_ratio': random.uniform(0.5, 2.0),
            'high_52w': max([d['High'] for d in historical_data]),
            'low_52w': min([d['Low'] for d in historical_data]),
            'last_updated': datetime.now().isoformat(),
            'historical_data': historical_data,
            'source': 'mock_bist'
        }
        
        mock_data.append(stock_data)
    
    return mock_data

def test_bist_solutions():
    """BIST çözümlerini test eder"""
    print("🔍 BIST Hisse API Çözümleri Test Ediliyor...")
    print("=" * 60)
    print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Investing.com test
    print("\n🔍 Investing.com test ediliyor...")
    investing_data = get_bist_data_from_investing()
    if investing_data:
        print(f"✅ Investing.com: {len(investing_data)} hisse bulundu")
        for stock in investing_data[:3]:
            print(f"   📊 {stock['symbol']}: {stock['price']} ({stock['change']})")
    else:
        print("❌ Investing.com: Veri çekilemedi")
    
    # 2. Bigpara test
    print("\n🔍 Bigpara test ediliyor...")
    bigpara_data = get_bist_data_from_bigpara()
    if bigpara_data:
        print(f"✅ Bigpara: {len(bigpara_data)} hisse bulundu")
        for stock in bigpara_data[:3]:
            print(f"   📊 {stock['symbol']}: {stock['price']} ({stock['change']})")
    else:
        print("❌ Bigpara: Veri çekilemedi")
    
    # 3. Foreks test
    print("\n🔍 Foreks test ediliyor...")
    foreks_data = get_bist_data_from_foreks()
    if foreks_data:
        print(f"✅ Foreks: {len(foreks_data)} hisse bulundu")
        for stock in foreks_data[:3]:
            print(f"   📊 {stock['symbol']}: {stock['price']} ({stock['change']})")
    else:
        print("❌ Foreks: Veri çekilemedi")
    
    # 4. Mock data test
    print("\n🔍 Mock data test ediliyor...")
    mock_data = create_mock_bist_data()
    print(f"✅ Mock data: {len(mock_data)} hisse oluşturuldu")
    for stock in mock_data[:3]:
        print(f"   📊 {stock['symbol']}: ${stock['current_price']:.2f} ({stock['daily_change']:+.2f}%)")
    
    print("\n" + "=" * 60)
    print("📊 ÖNERİLER")
    print("=" * 60)
    print("1. Web scraping ile BIST verisi çekin")
    print("2. Mock data kullanarak sistem çalışır tutun")
    print("3. Premium API planlarına geçmeyi düşünün")
    print("4. BIST için özel API servisleri araştırın")
    print("=" * 60)

if __name__ == "__main__":
    test_bist_solutions() 