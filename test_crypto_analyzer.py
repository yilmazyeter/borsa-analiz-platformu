#!/usr/bin/env python3
"""
Crypto Analyzer Test Dosyası
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.crypto_analyzer import CryptoAnalyzer
import time

def test_crypto_analyzer():
    """Crypto analyzer'ı test eder"""
    print("🪙 Crypto Analyzer Test Başlıyor...")
    
    # Crypto analyzer'ı başlat
    analyzer = CryptoAnalyzer()
    
    # 1. USDT çiftlerini al
    print("\n1. USDT çiftleri alınıyor...")
    usdt_pairs = analyzer.get_all_usdt_pairs()
    print(f"✅ {len(usdt_pairs)} USDT çifti bulundu")
    
    if usdt_pairs:
        print(f"İlk 10 çift: {usdt_pairs[:10]}")
    
    # 2. Belirli bir coin'in verilerini al
    print("\n2. BTCUSDT verisi alınıyor...")
    btc_data = analyzer.get_coin_data("BTCUSDT")
    
    if btc_data:
        print(f"✅ BTCUSDT verisi alındı")
        print(f"Güncel fiyat: ${btc_data['current_price']:.2f}")
        print(f"24h değişim: {btc_data['change_24h']:.2f}%")
        print(f"7g değişim: {btc_data['change_7d']:.2f}%")
        print(f"24h hacim: ${btc_data['volume_24h']/1000000:.1f}M")
    else:
        print("❌ BTCUSDT verisi alınamadı")
    
    # 3. Fırsat analizi
    print("\n3. Fırsat analizi yapılıyor...")
    opportunities = analyzer.find_opportunities(min_score=10.0, max_results=5)
    
    if opportunities:
        print(f"✅ {len(opportunities)} fırsat bulundu")
        for i, opp in enumerate(opportunities[:3]):
            print(f"  {i+1}. {opp['symbol']}: Skor={opp['opportunity_score']:.1f}, "
                  f"Fiyat=${opp['current_price']:.6f}, Değişim={opp['change_7d']:.1f}%")
    else:
        print("❌ Fırsat bulunamadı")
    
    # 4. Teknik göstergeler
    print("\n4. Teknik göstergeler hesaplanıyor...")
    if btc_data and 'data' in btc_data:
        indicators = analyzer.calculate_technical_indicators(btc_data['data'])
        if indicators:
            print(f"✅ Teknik göstergeler hesaplandı")
            print(f"RSI: {indicators.get('rsi', 0):.1f}")
            print(f"SMA 20: {indicators.get('sma_20', 0):.2f}")
            print(f"EMA 12: {indicators.get('ema_12', 0):.2f}")
            print(f"MACD: {indicators.get('macd_line', 0):.6f}")
        else:
            print("❌ Teknik göstergeler hesaplanamadı")
    
    print("\n✅ Crypto Analyzer test tamamlandı!")

if __name__ == "__main__":
    test_crypto_analyzer() 