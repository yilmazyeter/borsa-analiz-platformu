#!/usr/bin/env python3
"""
Düzeltilmiş Sistem Test Scripti
Gerçek veri çekme sistemini test eder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.stock_scraper import StockScraper

def test_fixed_system():
    """Düzeltilmiş sistemi test eder"""
    print("🚀 DÜZELTİLMİŞ SİSTEM TEST EDİLİYOR")
    print("=" * 60)
    
    scraper = StockScraper()
    
    # Test hisseleri
    test_stocks = [
        # ABD hisseleri (Finnhub ile gerçek veri)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
        # BIST hisseleri (Geliştirilmiş mock data)
        'THYAO', 'GARAN', 'AKBNK', 'YAPI', 'KRDMD'
    ]
    
    results = {
        'real_data': [],
        'mock_data': [],
        'errors': []
    }
    
    for symbol in test_stocks:
        print(f"\n🔍 {symbol} test ediliyor...")
        
        try:
            data = scraper.get_stock_data(symbol, "30d")
            
            if data:
                if data['source'] == 'finnhub':
                    results['real_data'].append({
                        'symbol': symbol,
                        'price': data['current_price'],
                        'change': data['daily_change'],
                        'source': data['source']
                    })
                    print(f"✅ GERÇEK VERİ: {symbol} - ${data['current_price']:.2f} ({data['daily_change']:+.2f}%)")
                else:
                    results['mock_data'].append({
                        'symbol': symbol,
                        'price': data['current_price'],
                        'change': data['daily_change'],
                        'source': data['source'],
                        'currency': data.get('currency', 'USD'),
                        'is_bist': data.get('is_bist', False)
                    })
                    currency = data.get('currency', 'USD')
                    print(f"✅ MOCK DATA: {symbol} - {data['current_price']:.2f} {currency} ({data['daily_change']:+.2f}%)")
            else:
                results['errors'].append(symbol)
                print(f"❌ HATA: {symbol} - Veri alınamadı")
                
        except Exception as e:
            results['errors'].append(symbol)
            print(f"❌ HATA: {symbol} - {str(e)}")
    
    # Sonuçları özetle
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    
    print(f"✅ Gerçek Veri Çekilen: {len(results['real_data'])} hisse")
    for item in results['real_data']:
        print(f"   📊 {item['symbol']}: ${item['price']:.2f} ({item['change']:+.2f}%) - {item['source']}")
    
    print(f"\n✅ Mock Data Kullanılan: {len(results['mock_data'])} hisse")
    for item in results['mock_data']:
        currency = item['currency']
        print(f"   📊 {item['symbol']}: {item['price']:.2f} {currency} ({item['change']:+.2f}%) - {item['source']}")
    
    if results['errors']:
        print(f"\n❌ Hata Alan: {len(results['errors'])} hisse")
        for symbol in results['errors']:
            print(f"   ❌ {symbol}")
    
    print("\n" + "=" * 60)
    print("🎯 SİSTEM DURUMU")
    print("=" * 60)
    
    if len(results['real_data']) > 0:
        print("✅ ABD hisseleri için gerçek veri çekiliyor")
    else:
        print("❌ ABD hisseleri için gerçek veri çekilemiyor")
    
    if len(results['mock_data']) > 0:
        print("✅ BIST hisseleri için geliştirilmiş mock data çalışıyor")
    else:
        print("❌ Mock data sistemi çalışmıyor")
    
    if len(results['errors']) == 0:
        print("🎉 Tüm testler başarılı!")
    else:
        print(f"⚠️ {len(results['errors'])} hata var")
    
    print("=" * 60)

if __name__ == "__main__":
    test_fixed_system() 