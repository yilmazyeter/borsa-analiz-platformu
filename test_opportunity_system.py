#!/usr/bin/env python3
"""
Fırsat Analizi ve Hayali Alım-Satım Sistemi Test Dosyası
"""

import sys
import os
from datetime import datetime, timedelta

# Proje modüllerini import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.opportunity_analyzer import OpportunityAnalyzer
from data.data_manager import DataManager

def test_opportunity_analyzer():
    """Fırsat analizi testi"""
    print("🧪 FIRSAT ANALİZİ TESTİ")
    print("=" * 50)
    
    analyzer = OpportunityAnalyzer()
    
    # Test 1: BIST fırsat analizi
    print("\n1️⃣ BIST Fırsat Analizi Testi")
    print("-" * 30)
    
    try:
        opportunities = analyzer.get_real_time_opportunities(market='bist', min_decline=30)
        print(f"✅ BIST analizi tamamlandı: {len(opportunities)} fırsat bulundu")
        
        if opportunities:
            print("\n🔥 En İyi BIST Fırsatları:")
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"{i}. {opp['symbol']}: %{opp['total_change']:.1f} düşüş, Skor: {opp['opportunity_score']:.1f}")
    except Exception as e:
        print(f"❌ BIST analizi hatası: {str(e)}")
    
    # Test 2: ABD fırsat analizi
    print("\n2️⃣ ABD Fırsat Analizi Testi")
    print("-" * 30)
    
    try:
        opportunities = analyzer.get_real_time_opportunities(market='us', min_decline=30)
        print(f"✅ ABD analizi tamamlandı: {len(opportunities)} fırsat bulundu")
        
        if opportunities:
            print("\n🔥 En İyi ABD Fırsatları:")
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"{i}. {opp['symbol']}: %{opp['total_change']:.1f} düşüş, Skor: {opp['opportunity_score']:.1f}")
    except Exception as e:
        print(f"❌ ABD analizi hatası: {str(e)}")
    
    # Test 3: Takip listesine ekleme
    print("\n3️⃣ Takip Listesi Ekleme Testi")
    print("-" * 30)
    
    try:
        # Örnek fırsatlar oluştur
        sample_opportunities = [
            {
                'symbol': 'TEST1.IS',
                'market': 'BIST',
                'opportunity_score': 85.5,
                'current_price': 25.50,
                'total_change': -45.2
            },
            {
                'symbol': 'TEST2',
                'market': 'US',
                'opportunity_score': 78.3,
                'current_price': 45.20,
                'total_change': -52.1
            }
        ]
        
        result = analyzer.add_to_watchlist_from_opportunities(sample_opportunities, 2)
        if result:
            print(f"✅ Takip listesi ekleme başarılı: {result['added_count']} hisse eklendi")
        else:
            print("❌ Takip listesi ekleme başarısız")
    except Exception as e:
        print(f"❌ Takip listesi ekleme hatası: {str(e)}")

def test_data_manager():
    """Veri yöneticisi testi"""
    print("\n\n🧪 VERİ YÖNETİCİSİ TESTİ")
    print("=" * 50)
    
    data_manager = DataManager()
    
    # Test 1: Kullanıcı bakiyesi
    print("\n1️⃣ Kullanıcı Bakiyesi Testi")
    print("-" * 30)
    
    try:
        gokhan_balance = data_manager.get_user_balance("gokhan")
        yilmaz_balance = data_manager.get_user_balance("yilmaz")
        
        print(f"✅ Gökhan bakiyesi: {gokhan_balance:,.2f} TL")
        print(f"✅ Yılmaz bakiyesi: {yilmaz_balance:,.2f} TL")
    except Exception as e:
        print(f"❌ Bakiye testi hatası: {str(e)}")
    
    # Test 2: Portföy işlemleri
    print("\n2️⃣ Portföy İşlemleri Testi")
    print("-" * 30)
    
    try:
        # Test alım işlemi
        symbol = "TEST.IS"
        quantity = 100
        price = 25.50
        
        success, message = data_manager.buy_stock("gokhan", symbol, quantity, price)
        print(f"✅ Alım işlemi: {message}")
        
        # Portföyü kontrol et
        portfolio = data_manager.get_user_portfolio("gokhan")
        print(f"✅ Portföy: {len(portfolio)} hisse")
        
        if portfolio:
            for item in portfolio:
                print(f"   • {item['symbol']}: {item['shares']} adet @ {item['avg_price']:.2f} TL")
        
        # Test satım işlemi
        sell_quantity = 50
        sell_price = 26.00
        
        success, message = data_manager.sell_stock("gokhan", symbol, sell_quantity, sell_price)
        print(f"✅ Satım işlemi: {message}")
        
    except Exception as e:
        print(f"❌ Portföy işlemleri hatası: {str(e)}")
    
    # Test 3: İşlem geçmişi
    print("\n3️⃣ İşlem Geçmişi Testi")
    print("-" * 30)
    
    try:
        transactions = data_manager.get_user_transactions("gokhan", 10)
        print(f"✅ İşlem geçmişi: {len(transactions)} kayıt")
        
        for trans in transactions:
            print(f"   • {trans['date']}: {trans['type']} {trans['shares']} {trans['symbol']} @ {trans['price']:.2f} TL")
    except Exception as e:
        print(f"❌ İşlem geçmişi hatası: {str(e)}")
    
    # Test 4: Performans takibi
    print("\n4️⃣ Performans Takibi Testi")
    print("-" * 30)
    
    try:
        performance = data_manager.get_performance_tracking("gokhan")
        print(f"✅ Performans takibi: {len(performance)} kayıt")
        
        for perf in performance:
            status = "🟢" if perf['profit_loss'] >= 0 else "🔴"
            print(f"   {status} {perf['symbol']}: {perf['profit_loss']:+,.2f} TL ({perf['profit_loss_percent']:+.2f}%) - {perf['days_held']} gün")
    except Exception as e:
        print(f"❌ Performans takibi hatası: {str(e)}")

def test_integration():
    """Entegrasyon testi"""
    print("\n\n🧪 ENTEGRASYON TESTİ")
    print("=" * 50)
    
    analyzer = OpportunityAnalyzer()
    data_manager = DataManager()
    
    print("\n🔄 Fırsat Analizi → Takip Listesi → Alım İşlemi Akışı")
    print("-" * 50)
    
    try:
        # 1. Fırsat analizi
        print("1️⃣ Fırsat analizi yapılıyor...")
        opportunities = analyzer.get_real_time_opportunities(market='both', min_decline=20)
        
        if not opportunities:
            print("❌ Test için fırsat bulunamadı")
            return
        
        print(f"✅ {len(opportunities)} fırsat bulundu")
        
        # 2. En iyi fırsatı seç
        best_opp = opportunities[0]
        print(f"2️⃣ En iyi fırsat: {best_opp['symbol']} (Skor: {best_opp['opportunity_score']:.1f})")
        
        # 3. Takip listesine ekle
        print("3️⃣ Takip listesine ekleniyor...")
        success = data_manager.add_to_watchlist(best_opp['symbol'], f"{best_opp['symbol']} - {best_opp['market']}")
        
        if success:
            print(f"✅ {best_opp['symbol']} takip listesine eklendi")
        else:
            print(f"⚠️ {best_opp['symbol']} zaten takip listesinde")
        
        # 4. Alım işlemi
        print("4️⃣ Alım işlemi yapılıyor...")
        quantity = 50
        price = best_opp['current_price']
        
        success, message = data_manager.buy_stock("gokhan", best_opp['symbol'], quantity, price)
        
        if success:
            print(f"✅ Alım başarılı: {message}")
            print(f"   📊 {quantity} adet {best_opp['symbol']} @ {price:.2f} {best_opp['currency']}")
        else:
            print(f"❌ Alım başarısız: {message}")
        
        # 5. Sonuçları kontrol et
        print("5️⃣ Sonuçlar kontrol ediliyor...")
        
        # Takip listesi
        watchlist = data_manager.get_watchlist()
        watchlist_symbols = [item['symbol'] for item in watchlist]
        if best_opp['symbol'] in watchlist_symbols:
            print(f"✅ {best_opp['symbol']} takip listesinde mevcut")
        else:
            print(f"❌ {best_opp['symbol']} takip listesinde bulunamadı")
        
        # Portföy
        portfolio = data_manager.get_user_portfolio("gokhan")
        portfolio_symbols = [item['symbol'] for item in portfolio]
        if best_opp['symbol'] in portfolio_symbols:
            print(f"✅ {best_opp['symbol']} portföyde mevcut")
        else:
            print(f"❌ {best_opp['symbol']} portföyde bulunamadı")
        
        # Performans takibi
        performance = data_manager.get_performance_tracking("gokhan")
        perf_symbols = [p['symbol'] for p in performance]
        if best_opp['symbol'] in perf_symbols:
            print(f"✅ {best_opp['symbol']} performans takibinde mevcut")
        else:
            print(f"❌ {best_opp['symbol']} performans takibinde bulunamadı")
        
    except Exception as e:
        print(f"❌ Entegrasyon testi hatası: {str(e)}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 FIRSAT ANALİZİ VE HAYALİ ALIM-SATIM SİSTEMİ TESTİ")
    print("=" * 70)
    print(f"📅 Test Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Test 1: Fırsat analizi
        test_opportunity_analyzer()
        
        # Test 2: Veri yöneticisi
        test_data_manager()
        
        # Test 3: Entegrasyon
        test_integration()
        
        print("\n" + "=" * 70)
        print("✅ TÜM TESTLER TAMAMLANDI!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {str(e)}")
        print("=" * 70)

if __name__ == "__main__":
    main() 