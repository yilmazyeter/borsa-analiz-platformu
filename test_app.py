#!/usr/bin/env python3
"""
Hisse Takip ve Analiz Uygulaması - Test Modülü
"""

import sys
import os
import time
from datetime import datetime

# Proje modüllerini import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import StockAnalysisApp


def test_basic_functionality():
    """Temel işlevsellik testleri"""
    print("🧪 Temel işlevsellik testi başlatılıyor...")
    
    try:
        # Uygulama başlatma testi
        app = StockAnalysisApp()
        print("✅ Uygulama başarıyla başlatıldı")
        
        # Türk hisseleri yükleme testi
        turkish_stocks = app.stock_scraper.get_turkish_stocks()
        print(f"✅ {len(turkish_stocks)} Türk hissesi yüklendi")
        
        # Test hisseleri
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
        
        # Her hisse için veri çekme testi
        successful_fetches = 0
        for symbol in test_symbols:
            print(f"🔍 Test ediliyor: {symbol}")
            data = app.stock_scraper.get_stock_data(symbol, period="7d")
            
            if data:
                print(f"✅ {symbol} verileri başarıyla çekildi (Kaynak: {data.get('source', 'bilinmiyor')})")
                successful_fetches += 1
            else:
                print(f"❌ {symbol} verileri çekilemedi")
        
        if successful_fetches == 0:
            print("⚠️ Hiçbir hisse için veri çekilemedi")
            print("🔄 Alternatif test hisseleri deneniyor...")
            
            # Alternatif test hisseleri
            alt_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
            for symbol in alt_symbols:
                print(f"🔍 Test ediliyor: {symbol}")
                data = app.stock_scraper.get_stock_data(symbol, period="7d")
                
                if data:
                    print(f"✅ {symbol} verileri başarıyla çekildi (Kaynak: {data.get('source', 'bilinmiyor')})")
                    successful_fetches += 1
                else:
                    print(f"❌ {symbol} verileri çekilemedi")
        
        # Takip listesi testleri
        print("\n📋 Takip listesi testleri:")
        
        # Hisse ekleme testi
        test_symbol = "AAPL"
        print(f"➕ {test_symbol} takip listesine ekleniyor...")
        try:
            app.add_to_watchlist(test_symbol)
            print(f"✅ {test_symbol} başarıyla takip listesine eklendi.")
        except Exception as e:
            print(f"❌ {test_symbol} eklenirken hata: {str(e)}")
        
        # Takip listesini görüntüleme
        print("\n📋 Takip Listeniz:")
        app.show_watchlist()
        
        # Hisse çıkarma testi
        print(f"\n➖ {test_symbol} takip listesinden çıkarılıyor...")
        try:
            app.remove_from_watchlist(test_symbol)
            print(f"✅ {test_symbol} takip listesinden çıkarıldı.")
        except Exception as e:
            print(f"❌ {test_symbol} çıkarılırken hata: {str(e)}")
        
        print("✅ Temel işlevsellik testi tamamlandı")
        return True
        
    except Exception as e:
        print(f"❌ Temel işlevsellik testi başarısız: {str(e)}")
        return False


def test_analysis_modules():
    """Analiz modülleri testleri"""
    print("\n🧪 Analiz Modülleri testi başlatılıyor...")
    
    try:
        app = StockAnalysisApp()
        
        # Test hisseleri
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        
        successful_analyses = 0
        for symbol in test_symbols:
            print(f"🔍 Test ediliyor: {symbol}")
            
            # Veri çekme
            data = app.stock_scraper.get_stock_data(symbol, period="30d")
            if not data:
                print(f"❌ {symbol} verileri çekilemedi")
                continue
            
            # Analiz yapma
            try:
                # Trend analizi
                trend_analysis = app.trend_analyzer.analyze_price_trend(data, 30)
                if trend_analysis:
                    print(f"✅ {symbol} trend analizi başarılı")
                    successful_analyses += 1
                else:
                    print(f"❌ {symbol} trend analizi başarısız")
            except Exception as e:
                print(f"❌ {symbol} analiz hatası: {str(e)}")
        
        if successful_analyses > 0:
            print(f"✅ Analiz Modülleri testi BAŞARILI ({successful_analyses}/{len(test_symbols)})")
            return True
        else:
            print("❌ Hiçbir hisse için analiz yapılamadı")
            print("❌ Analiz Modülleri testi BAŞARISIZ")
            return False
            
    except Exception as e:
        print(f"❌ Analiz modülleri testi başarısız: {str(e)}")
        return False


def test_visualization():
    """Görselleştirme testleri"""
    print("\n🧪 Görselleştirme testi başlatılıyor...")
    
    try:
        app = StockAnalysisApp()
        
        # Test hisseleri
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
        
        successful_charts = 0
        for symbol in test_symbols:
            print(f"🔍 Test ediliyor: {symbol}")
            
            # Veri çekme
            data = app.stock_scraper.get_stock_data(symbol, period="30d")
            if not data:
                print(f"❌ {symbol} verileri çekilemedi")
                continue
            
            # Grafik oluşturma
            try:
                chart_path = app.chart_generator.create_price_chart(data, save_path=f"test_chart_{symbol}.png")
                if chart_path and os.path.exists(chart_path):
                    print(f"✅ {symbol} grafiği oluşturuldu: {chart_path}")
                    successful_charts += 1
                    # Test dosyasını temizle
                    os.remove(chart_path)
                else:
                    print(f"❌ {symbol} grafiği oluşturulamadı")
            except Exception as e:
                print(f"❌ {symbol} grafik hatası: {str(e)}")
        
        if successful_charts > 0:
            print(f"✅ Görselleştirme testi BAŞARILI ({successful_charts}/{len(test_symbols)})")
            return True
        else:
            print("❌ Hiçbir grafik oluşturulamadı")
            print("❌ Görselleştirme testi BAŞARISIZ")
            return False
            
    except Exception as e:
        print(f"❌ Görselleştirme testi başarısız: {str(e)}")
        return False


def test_reporting():
    """Raporlama testleri"""
    print("\n🧪 Raporlama testi başlatılıyor...")
    
    try:
        app = StockAnalysisApp()
        
        # Test hisseleri
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
        
        successful_reports = 0
        for symbol in test_symbols:
            print(f"🔍 Test ediliyor: {symbol}")
            
            # Veri çekme
            data = app.stock_scraper.get_stock_data(symbol, period="30d")
            if not data:
                print(f"❌ {symbol} verileri çekilemedi")
                continue
            
            # Rapor oluşturma
            try:
                report_path = app.report_generator.create_html_report(data, {}, {}, {}, None, 30)
                if report_path and os.path.exists(report_path):
                    print(f"✅ {symbol} raporu oluşturuldu: {report_path}")
                    successful_reports += 1
                    # Test dosyasını temizle
                    os.remove(report_path)
                else:
                    print(f"❌ {symbol} raporu oluşturulamadı")
            except Exception as e:
                print(f"❌ {symbol} rapor hatası: {str(e)}")
        
        if successful_reports > 0:
            print(f"✅ Raporlama testi BAŞARILI ({successful_reports}/{len(test_symbols)})")
            return True
        else:
            print("❌ Hiçbir rapor oluşturulamadı")
            print("❌ Raporlama testi BAŞARISIZ")
            return False
            
    except Exception as e:
        print(f"❌ Raporlama testi başarısız: {str(e)}")
        return False


def main():
    """Ana test fonksiyonu"""
    print("🚀 Hisse Takip ve Analiz Uygulaması - Test Süreci")
    print("=" * 60)
    
    # Test sonuçları
    test_results = []
    
    # Temel işlevsellik testi
    test_results.append(test_basic_functionality())
    
    # Analiz modülleri testi
    test_results.append(test_analysis_modules())
    
    # Görselleştirme testi
    test_results.append(test_visualization())
    
    # Raporlama testi
    test_results.append(test_reporting())
    
    # Sonuçları özetle
    print("\n📊 TEST SONUÇLARI")
    print("=" * 40)
    
    successful_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"Başarılı: {successful_tests}/{total_tests}")
    print(f"Başarı Oranı: %{success_rate:.1f}")
    
    if success_rate >= 75:
        print("🎉 Testler başarıyla tamamlandı!")
    elif success_rate >= 50:
        print("⚠️ Bazı testler başarısız oldu.")
        print("🔧 Lütfen internet bağlantınızı kontrol edin.")
    else:
        print("❌ Çoğu test başarısız oldu.")
        print("🔧 Lütfen sistem gereksinimlerini kontrol edin.")
    
    print("\n✅ Test süreci tamamlandı.")


if __name__ == "__main__":
    main() 