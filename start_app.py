#!/usr/bin/env python3
"""
Borsa Analiz Platformu - Otomatik Başlatma Scripti
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_banner():
    """Uygulama banner'ını yazdır"""
    print("=" * 70)
    print("🚀 BORSA ANALİZ PLATFORMU - OTOMATİK BAŞLATMA")
    print("=" * 70)
    print(f"📅 Başlatma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def check_dependencies():
    """Gerekli kütüphaneleri kontrol et"""
    print("🔍 Gerekli kütüphaneler kontrol ediliyor...")
    
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'yfinance', 'plotly', 
        'requests', 'textblob', 'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Eksik")
    
    if missing_packages:
        print(f"\n⚠️ Eksik kütüphaneler: {', '.join(missing_packages)}")
        print("📦 Kurulum için: pip install -r requirements.txt")
        return False
    
    print("✅ Tüm kütüphaneler mevcut!")
    return True

def start_terminal_app():
    """Terminal uygulamasını başlat"""
    print("\n🖥️ Terminal Uygulaması Başlatılıyor...")
    print("-" * 50)
    
    try:
        # Ana uygulamayı başlat
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Terminal uygulaması kapatıldı.")
    except Exception as e:
        print(f"❌ Terminal uygulaması hatası: {str(e)}")

def start_web_app():
    """Web uygulamasını başlat"""
    print("\n🌐 Web Uygulaması Başlatılıyor...")
    print("-" * 50)
    print("📱 Tarayıcınızda http://localhost:8501 adresini açın")
    print("🔄 Web uygulamasını durdurmak için Ctrl+C")
    print("-" * 50)
    
    try:
        # Streamlit uygulamasını başlat
        subprocess.run(["streamlit", "run", "web_app.py", "--server.port", "8501"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web uygulaması kapatıldı.")
    except Exception as e:
        print(f"❌ Web uygulaması hatası: {str(e)}")

def run_tests():
    """Testleri çalıştır"""
    print("\n🧪 Sistem Testleri Çalıştırılıyor...")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "test_opportunity_system.py"], check=True)
        print("✅ Testler başarıyla tamamlandı!")
    except Exception as e:
        print(f"❌ Test hatası: {str(e)}")

def show_menu():
    """Ana menüyü göster"""
    print("\n📋 BAŞLATMA MENÜSÜ")
    print("=" * 40)
    print("1. 🖥️ Terminal Uygulaması")
    print("2. 🌐 Web Uygulaması")
    print("3. 🧪 Sistem Testleri")
    print("4. 🔄 Her İkisini Başlat")
    print("5. 📊 Hızlı Fırsat Analizi")
    print("0. ❌ Çıkış")
    print("=" * 40)

def quick_opportunity_analysis():
    """Hızlı fırsat analizi"""
    print("\n⚡ HIZLI FIRSAT ANALİZİ")
    print("-" * 50)
    
    try:
        from analysis.opportunity_analyzer import OpportunityAnalyzer
        
        analyzer = OpportunityAnalyzer()
        
        print("🔍 BIST hisseleri analiz ediliyor...")
        bist_opps = analyzer.get_real_time_opportunities(market='bist', min_decline=40)
        
        print("🔍 ABD hisseleri analiz ediliyor...")
        us_opps = analyzer.get_real_time_opportunities(market='us', min_decline=40)
        
        all_opps = bist_opps + us_opps
        all_opps.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        print(f"\n✅ Toplam {len(all_opps)} fırsat bulundu!")
        print("\n🔥 En İyi 5 Fırsat:")
        print("-" * 60)
        print(f"{'Sıra':<4} {'Sembol':<12} {'Piyasa':<6} {'Fiyat':<10} {'Değişim':<12} {'Skor':<8}")
        print("-" * 60)
        
        for i, opp in enumerate(all_opps[:5], 1):
            print(f"{i:<4} {opp['symbol']:<12} {opp['market']:<6} "
                  f"{opp['current_price']:<10.2f} {opp['total_change']:<12.1f}% "
                  f"{opp['opportunity_score']:<8.1f}")
        
        # Takip listesine ekleme seçeneği
        if all_opps:
            print(f"\n📋 En iyi 3 fırsatı takip listesine eklemek ister misiniz? (y/n): ", end="")
            response = input().lower().strip()
            
            if response in ['y', 'yes', 'evet', 'e']:
                result = analyzer.add_to_watchlist_from_opportunities(all_opps, 3)
                if result:
                    print(f"✅ {result['added_count']} hisse takip listesine eklendi!")
                    for stock in result['added_stocks']:
                        print(f"   • {stock['symbol']} ({stock['market']})")
        
    except Exception as e:
        print(f"❌ Hızlı analiz hatası: {str(e)}")

def start_both_apps():
    """Her iki uygulamayı da başlat"""
    print("\n🔄 Her İki Uygulama Başlatılıyor...")
    print("-" * 50)
    
    try:
        # Web uygulamasını arka planda başlat
        web_process = subprocess.Popen(["streamlit", "run", "web_app.py", "--server.port", "8501"])
        
        print("✅ Web uygulaması arka planda başlatıldı (http://localhost:8501)")
        print("⏳ 3 saniye bekleniyor...")
        time.sleep(3)
        
        # Terminal uygulamasını başlat
        print("🖥️ Terminal uygulaması başlatılıyor...")
        subprocess.run([sys.executable, "main.py"], check=True)
        
        # Web uygulamasını durdur
        web_process.terminate()
        print("👋 Web uygulaması durduruldu.")
        
    except KeyboardInterrupt:
        print("\n👋 Uygulamalar kapatıldı.")
    except Exception as e:
        print(f"❌ Başlatma hatası: {str(e)}")

def main():
    """Ana fonksiyon"""
    print_banner()
    
    # Kütüphaneleri kontrol et
    if not check_dependencies():
        print("\n❌ Gerekli kütüphaneler eksik. Lütfen önce kurulum yapın.")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSeçiminizi yapın (0-5): ").strip()
            
            if choice == '0':
                print("👋 Görüşürüz!")
                break
            elif choice == '1':
                start_terminal_app()
            elif choice == '2':
                start_web_app()
            elif choice == '3':
                run_tests()
            elif choice == '4':
                start_both_apps()
            elif choice == '5':
                quick_opportunity_analysis()
            else:
                print("❌ Geçersiz seçim!")
                
        except KeyboardInterrupt:
            print("\n👋 Görüşürüz!")
            break
        except Exception as e:
            print(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    main() 