#!/usr/bin/env python3
"""
Basit Crypto Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.crypto_analyzer import CryptoAnalyzer

def simple_test():
    print("🪙 Basit Crypto Test Başlıyor...")
    
    try:
        # Crypto analyzer'ı başlat
        analyzer = CryptoAnalyzer()
        print("✅ Crypto Analyzer başlatıldı")
        
        # Sadece BTCUSDT test et
        print("\n📊 BTCUSDT verisi alınıyor...")
        btc_data = analyzer.get_coin_data("BTCUSDT", limit=24)  # Sadece 24 saat
        
        if btc_data:
            print(f"✅ BTCUSDT verisi alındı!")
            print(f"💰 Güncel fiyat: ${btc_data['current_price']:.2f}")
            print(f"📈 24h değişim: {btc_data['change_24h']:.2f}%")
            print(f"📊 7g değişim: {btc_data['change_7d']:.2f}%")
            print(f"💎 24h hacim: ${btc_data['volume_24h']/1000000:.1f}M")
            
            # Fırsat analizi
            print("\n🎯 Fırsat analizi yapılıyor...")
            opportunity = analyzer.analyze_coin_opportunity(btc_data)
            
            if opportunity:
                print(f"✅ Fırsat analizi tamamlandı!")
                print(f"📊 Fırsat skoru: {opportunity.get('opportunity_score', 0):.1f}")
                print(f"🎯 Fırsat tipi: {opportunity.get('opportunity_type', 'N/A')}")
                print(f"💡 Öneri: {opportunity.get('recommendation', 'N/A')}")
                if opportunity.get('rsi'):
                    print(f"📈 RSI: {opportunity['rsi']:.1f}")
            
            # Teknik göstergeler
            print("\n📊 Teknik göstergeler hesaplanıyor...")
            if 'data' in btc_data:
                indicators = analyzer.calculate_technical_indicators(btc_data['data'])
                if indicators:
                    print(f"✅ Teknik göstergeler hesaplandı!")
                    print(f"📈 RSI: {indicators.get('rsi', 0):.1f}")
                    print(f"📊 SMA 20: {indicators.get('sma_20', 0):.2f}")
                    print(f"📈 EMA 12: {indicators.get('ema_12', 0):.2f}")
                    print(f"📊 MACD: {indicators.get('macd_line', 0):.6f}")
        
        else:
            print("❌ BTCUSDT verisi alınamadı")
        
        print("\n✅ Basit test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test() 