#!/usr/bin/env python3
"""
Çoklu Coin Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.crypto_analyzer import CryptoAnalyzer

def multi_coin_test():
    print("🪙 Çoklu Coin Test Başlıyor...")
    
    try:
        # Crypto analyzer'ı başlat
        analyzer = CryptoAnalyzer()
        print("✅ Crypto Analyzer başlatıldı")
        
        # Test edilecek coinler
        test_coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        
        for coin in test_coins:
            print(f"\n📊 {coin} analiz ediliyor...")
            
            try:
                # Coin verisini al
                coin_data = analyzer.get_coin_data(coin, limit=24)
                
                if coin_data:
                    print(f"✅ {coin} verisi alındı!")
                    print(f"💰 Fiyat: ${coin_data['current_price']:.6f}")
                    print(f"📈 24h: {coin_data['change_24h']:+.2f}%")
                    print(f"📊 7g: {coin_data['change_7d']:+.2f}%")
                    print(f"💎 Hacim: ${coin_data['volume_24h']/1000000:.1f}M")
                    
                    # Fırsat analizi
                    opportunity = analyzer.analyze_coin_opportunity(coin_data)
                    if opportunity:
                        print(f"🎯 Skor: {opportunity.get('opportunity_score', 0):.1f}")
                        print(f"💡 Öneri: {opportunity.get('recommendation', 'N/A')}")
                    
                    print("-" * 50)
                
                else:
                    print(f"❌ {coin} verisi alınamadı")
                
            except Exception as e:
                print(f"❌ {coin} analizi sırasında hata: {str(e)}")
        
        print("\n✅ Çoklu coin test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {str(e)}")

if __name__ == "__main__":
    multi_coin_test() 