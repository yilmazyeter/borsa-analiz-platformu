#!/usr/bin/env python3
"""
24 Saatlik Kazanç Analizi Test - Uzun Düşüşten Sonra Artış Potansiyeli
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.crypto_analyzer import CryptoAnalyzer

def test_24h_profit_analysis():
    print("💰 24 Saatlik Kazanç Analizi Test Başlıyor...")
    print("🎯 Hedef: Uzun süredir düşüşte olan ama artış potansiyeli olan coinler")
    
    try:
        # Crypto analyzer'ı başlat
        analyzer = CryptoAnalyzer()
        print("✅ Crypto Analyzer başlatıldı")
        
        # 24 saatlik kazanç fırsatlarını bul
        print("\n🔍 24 saatlik kazanç fırsatları aranıyor...")
        profit_opportunities = analyzer.find_24h_profit_opportunities(min_score=25.0, max_results=15)
        
        if profit_opportunities:
            print(f"✅ {len(profit_opportunities)} 24 saatlik kazanç fırsatı bulundu!")
            print("\n📊 Bulunan 24 Saatlik Kazanç Fırsatları:")
            print("-" * 120)
            
            for i, opp in enumerate(profit_opportunities, 1):
                print(f"{i:2d}. {opp['symbol']:12s} | Skor: {opp['profit_score']:5.1f} | Tavsiye: {opp['recommendation']:12s} | Güven: {opp['confidence']:8s}")
                print(f"    Fiyat: ${opp['current_price']:10.6f} | Hedef: ${opp['target_price']:10.6f} | Potansiyel: {opp['potential_gain_percent']:+6.2f}%")
                print(f"    24h: {opp['change_24h']:+6.2f}% | 7g: {opp['change_7d']:+6.2f}% | RSI: {opp['rsi']:5.1f} | Hacim: ${opp['volume_24h']/1000000:6.1f}M")
                
                # Özel durumlar
                status_flags = []
                if opp.get('long_term_drop', False):
                    status_flags.append("📉 Uzun vadeli düşüş")
                if opp.get('recovery_started', False):
                    status_flags.append("📈 Toparlanma başladı")
                
                if status_flags:
                    print(f"    Durum: {' | '.join(status_flags)}")
                
                if opp['reasoning']:
                    print(f"    Sebepler: {', '.join(opp['reasoning'])}")
                print()
            
            # En iyi fırsatlar
            print("🔥 En İyi 5 24 Saatlik Kazanç Fırsatı:")
            top_opportunities = sorted(profit_opportunities, key=lambda x: x['profit_score'], reverse=True)[:5]
            for i, opp in enumerate(top_opportunities, 1):
                print(f"   {i}. {opp['symbol']} - Skor: {opp['profit_score']:.1f} - Tavsiye: {opp['recommendation']} - Potansiyel: {opp['potential_gain_percent']:+.2f}%")
            
            # İstatistikler
            print("\n📈 24 Saatlik Kazanç İstatistikleri:")
            avg_score = sum(opp['profit_score'] for opp in profit_opportunities) / len(profit_opportunities)
            avg_potential = sum(opp['potential_gain_percent'] for opp in profit_opportunities) / len(profit_opportunities)
            kesinlikle_al_count = sum(1 for opp in profit_opportunities if opp['recommendation'] == "KESİNLİKLE AL")
            guclu_al_count = sum(1 for opp in profit_opportunities if opp['recommendation'] == "GÜÇLÜ AL")
            long_term_drop_count = sum(1 for opp in profit_opportunities if opp.get('long_term_drop', False))
            recovery_started_count = sum(1 for opp in profit_opportunities if opp.get('recovery_started', False))
            
            print(f"   Ortalama Skor: {avg_score:.1f}")
            print(f"   Ortalama Potansiyel Kazanç: {avg_potential:+.2f}%")
            print(f"   KESİNLİKLE AL: {kesinlikle_al_count} coin")
            print(f"   GÜÇLÜ AL: {guclu_al_count} coin")
            print(f"   Uzun Vadeli Düşüş: {long_term_drop_count} coin")
            print(f"   Toparlanma Başladı: {recovery_started_count} coin")
            
            # Ortalama düşüş analizi
            avg_7d_drop = sum(opp['change_7d'] for opp in profit_opportunities) / len(profit_opportunities)
            print(f"   Ortalama 7 Günlük Düşüş: {avg_7d_drop:.2f}%")
            
            # En güçlü sinyaller
            print("\n🎯 En Güçlü Sinyaller:")
            strong_signals = [opp for opp in profit_opportunities if opp['profit_score'] >= 50]
            for opp in strong_signals[:3]:
                print(f"   • {opp['symbol']}: {opp['recommendation']} (Skor: {opp['profit_score']:.1f})")
        
        else:
            print("❌ 24 saatlik kazanç fırsatı bulunamadı")
        
        print("\n✅ 24 saatlik kazanç analizi test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_24h_profit_analysis() 