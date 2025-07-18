#!/usr/bin/env python3
"""
Hisse Takip ve Derin Analiz Otomasyonu
Ana uygulama dosyası
"""

import os
import sys
import time
from datetime import datetime, timedelta
import json

# Modülleri import et
from scraper import StockScraper, NewsScraper, DataManager
from analysis import TrendAnalyzer, TechnicalAnalyzer, RiskAnalyzer, OpportunityAnalyzer
from visuals import ChartGenerator, ReportGenerator


class StockAnalysisApp:
    def __init__(self):
        """Ana uygulama sınıfı"""
        self.stock_scraper = StockScraper()
        self.news_scraper = NewsScraper()
        self.data_manager = DataManager()
        
        self.trend_analyzer = TrendAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.opportunity_analyzer = OpportunityAnalyzer()
        
        self.chart_generator = ChartGenerator()
        self.report_generator = ReportGenerator()
        
        print("🚀 Hisse Takip ve Derin Analiz Otomasyonu Başlatıldı")
        print("=" * 60)
    
    def find_declining_stocks(self, min_decline=80):
        """
        Son 1 yılda değer kaybetmiş hisseleri bulur
        
        Args:
            min_decline (float): Minimum düşüş yüzdesi
        
        Returns:
            list: Düşüş gösteren hisseler
        """
        print(f"🔍 Son 1 yılda %{min_decline}'den fazla değer kaybetmiş hisseler aranıyor...")
        
        turkish_stocks = self.stock_scraper.get_turkish_stocks()
        declining_stocks = self.stock_scraper.find_declining_stocks(turkish_stocks, min_decline)
        
        if declining_stocks:
            print(f"\n📉 {len(declining_stocks)} adet düşüş gösteren hisse bulundu:")
            print("-" * 80)
            print(f"{'Sembol':<10} {'Fiyat':<10} {'Yıllık Değişim':<15} {'Hacim Oranı':<15}")
            print("-" * 80)
            
            for stock in declining_stocks:
                print(f"{stock['symbol']:<10} {stock['current_price']:<10.2f} "
                      f"%{stock['yearly_change']:<14.2f} {stock['volume_ratio']:<15.2f}")
        else:
            print("❌ Belirtilen kriterlere uygun hisse bulunamadı.")
        
        return declining_stocks
    
    def add_to_watchlist(self, symbol):
        """
        Takip listesine hisse ekler
        
        Args:
            symbol (str): Hisse sembolü
        """
        print(f"➕ {symbol} takip listesine ekleniyor...")
        
        # Hisse bilgilerini al
        stock_info = self.stock_scraper.get_stock_info(symbol)
        name = stock_info['name'] if stock_info else ""
        
        if self.data_manager.add_to_watchlist(symbol, name):
            print(f"✅ {symbol} başarıyla takip listesine eklendi.")
        else:
            print(f"⚠️ {symbol} zaten takip listesinde mevcut.")
    
    def remove_from_watchlist(self, symbol):
        """
        Takip listesinden hisse çıkarır
        
        Args:
            symbol (str): Hisse sembolü
        """
        print(f"➖ {symbol} takip listesinden çıkarılıyor...")
        
        if self.data_manager.remove_from_watchlist(symbol):
            print(f"✅ {symbol} takip listesinden çıkarıldı.")
        else:
            print(f"❌ {symbol} takip listesinde bulunamadı.")
    
    def show_watchlist(self):
        """Takip listesini gösterir"""
        watchlist = self.data_manager.get_watchlist()
        
        if not watchlist:
            print("📋 Takip listeniz boş.")
            return
        
        print(f"\n📋 Takip Listeniz ({len(watchlist)} hisse):")
        print("-" * 60)
        print(f"{'Sembol':<10} {'Ad':<20} {'Eklenme Tarihi':<15}")
        print("-" * 60)
        
        for item in watchlist:
            added_date = datetime.fromisoformat(item['added_date']).strftime('%d/%m/%Y')
            print(f"{item['symbol']:<10} {item['name'][:18]:<20} {added_date:<15}")
    
    def analyze_stock(self, symbol, days=365):
        """
        Belirtilen hisseyi derinlemesine analiz eder
        
        Args:
            symbol (str): Hisse sembolü
            days (int): Analiz edilecek gün sayısı
        """
        print(f"🔬 {symbol} için derinlemesine analiz başlatılıyor...")
        print(f"📅 Analiz periyodu: Son {days} gün")
        print("-" * 60)
        
        # 1. Hisse verilerini çek
        print("📊 Hisse verileri çekiliyor...")
        stock_data = self.stock_scraper.get_stock_data(symbol, f"{days}d")
        
        if not stock_data:
            print(f"❌ {symbol} için veri çekilemedi.")
            return
        
        # Verileri kaydet
        self.data_manager.save_stock_data(stock_data)
        
        # 2. Haber sentiment analizi
        print("📰 Haber sentiment analizi yapılıyor...")
        news_sentiment = self.news_scraper.get_stock_news_sentiment(symbol, days)
        
        if news_sentiment:
            self.data_manager.save_news_data(news_sentiment)
        
        # 3. Trend analizi
        print("📈 Trend analizi yapılıyor...")
        trend_analysis = self.trend_analyzer.analyze_price_trend(stock_data, days)
        volume_analysis = self.trend_analyzer.analyze_volume_trend(stock_data, days)
        trend_recommendation = self.trend_analyzer.get_trend_recommendation(trend_analysis, volume_analysis)
        
        # 4. Teknik analiz
        print("🔧 Teknik göstergeler hesaplanıyor...")
        technical_analysis = self.technical_analyzer.analyze_technical_indicators(stock_data)
        technical_recommendation = self.technical_analyzer.get_technical_recommendation(technical_analysis)
        
        # 5. Risk analizi
        print("⚠️ Risk analizi yapılıyor...")
        risk_analysis = self.risk_analyzer.get_comprehensive_risk_analysis(stock_data, days)
        
        # 6. Fırsat analizi
        print("🎯 Fırsat analizi yapılıyor...")
        opportunity_analysis = self.opportunity_analyzer.get_comprehensive_opportunity_analysis(
            stock_data, technical_analysis, news_sentiment, days
        )
        
        # 7. Sonuçları göster
        self._display_analysis_results(symbol, stock_data, trend_analysis, technical_analysis, 
                                     risk_analysis, opportunity_analysis, news_sentiment)
        
        # 8. Grafikler oluştur
        print("\n📊 Grafikler oluşturuluyor...")
        self._create_charts(symbol, stock_data, technical_analysis, news_sentiment)
        
        # 9. Rapor oluştur
        print("📄 PDF raporu oluşturuluyor...")
        report_path = self.report_generator.create_stock_analysis_report(
            stock_data, technical_analysis, risk_analysis, opportunity_analysis, news_sentiment, days
        )
        print(f"✅ Rapor kaydedildi: {report_path}")
        
        # Analiz sonuçlarını kaydet
        if risk_analysis:
            self.data_manager.save_analysis_result(symbol, "risk", risk_analysis['recommendation'], 
                                                 risk_analysis['overall_risk_score'])
        
        if opportunity_analysis:
            self.data_manager.save_analysis_result(symbol, "opportunity", opportunity_analysis['recommendation'], 
                                                 opportunity_analysis['overall_opportunity_score'])
    
    def analyze_watchlist(self, days=7):
        """
        Takip listesindeki tüm hisseleri analiz eder
        
        Args:
            days (int): Analiz edilecek gün sayısı
        """
        watchlist = self.data_manager.get_watchlist()
        
        if not watchlist:
            print("📋 Takip listeniz boş. Önce hisse ekleyin.")
            return
        
        print(f"🔬 Takip listesindeki {len(watchlist)} hisse analiz ediliyor...")
        print(f"📅 Analiz periyodu: Son {days} gün")
        print("=" * 80)
        
        watchlist_results = []
        
        for i, item in enumerate(watchlist, 1):
            symbol = item['symbol']
            print(f"\n[{i}/{len(watchlist)}] {symbol} analiz ediliyor...")
            
            try:
                # Hisse verilerini çek
                stock_data = self.stock_scraper.get_stock_data(symbol, f"{days}d")
                
                if not stock_data:
                    print(f"❌ {symbol} için veri çekilemedi.")
                    continue
                
                # Hızlı analiz
                risk_analysis = self.risk_analyzer.get_comprehensive_risk_analysis(stock_data, days)
                news_sentiment = self.news_scraper.get_stock_news_sentiment(symbol, days)
                technical_analysis = self.technical_analyzer.analyze_technical_indicators(stock_data)
                opportunity_analysis = self.opportunity_analyzer.get_comprehensive_opportunity_analysis(
                    stock_data, technical_analysis, news_sentiment, days
                )
                
                # Sonuçları birleştir
                result = {
                    'symbol': symbol,
                    'current_price': stock_data['current_price'],
                    'daily_change': stock_data['daily_change'],
                    'current_volume': stock_data['current_volume'],
                    'risk_level': risk_analysis['overall_risk_level'] if risk_analysis else 'N/A',
                    'opportunity_level': opportunity_analysis['overall_opportunity_level'] if opportunity_analysis else 'N/A'
                }
                
                watchlist_results.append(result)
                
                # Kısa özet göster
                print(f"   💰 Fiyat: {stock_data['current_price']:.2f} TL (%{stock_data['daily_change']:.2f})")
                if risk_analysis:
                    print(f"   ⚠️ Risk: {risk_analysis['overall_risk_level']}")
                if opportunity_analysis:
                    print(f"   🎯 Fırsat: {opportunity_analysis['overall_opportunity_level']}")
                
            except Exception as e:
                print(f"❌ {symbol} analiz edilirken hata: {str(e)}")
                continue
        
        # Takip listesi raporu oluştur
        if watchlist_results:
            print(f"\n📄 Takip listesi raporu oluşturuluyor...")
            report_path = self.report_generator.create_watchlist_report(watchlist_results, days)
            print(f"✅ Rapor kaydedildi: {report_path}")
        
        # Özet göster
        self._display_watchlist_summary(watchlist_results)
    
    def _display_analysis_results(self, symbol, stock_data, trend_analysis, technical_analysis, 
                                risk_analysis, opportunity_analysis, news_sentiment):
        """Analiz sonuçlarını gösterir"""
        print(f"\n📊 {symbol} ANALİZ SONUÇLARI")
        print("=" * 60)
        
        # Temel bilgiler
        print(f"💰 Güncel Fiyat: {stock_data['current_price']:.2f} TL")
        print(f"📈 Günlük Değişim: %{stock_data['daily_change']:.2f}")
        print(f"📊 Yıllık Değişim: %{stock_data['yearly_change']:.2f}" if stock_data['yearly_change'] else "📊 Yıllık Değişim: N/A")
        print(f"📊 Hacim: {stock_data['current_volume']:,.0f}")
        
        # Trend analizi
        if trend_analysis:
            print(f"\n📈 TREND ANALİZİ:")
            print(f"   Yön: {trend_analysis['trend_direction']}")
            print(f"   Momentum: %{trend_analysis['momentum']:.2f}")
            print(f"   Volatilite: %{trend_analysis['volatility']:.2f}")
        
        # Risk analizi
        if risk_analysis:
            print(f"\n⚠️ RİSK ANALİZİ:")
            print(f"   Seviye: {risk_analysis['overall_risk_level']}")
            print(f"   Skor: {risk_analysis['overall_risk_score']:.1f}/100")
            print(f"   Öneri: {risk_analysis['recommendation']}")
        
        # Fırsat analizi
        if opportunity_analysis:
            print(f"\n🎯 FIRSAT ANALİZİ:")
            print(f"   Seviye: {opportunity_analysis['overall_opportunity_level']}")
            print(f"   Skor: {opportunity_analysis['overall_opportunity_score']:.1f}/100")
            print(f"   Öneri: {opportunity_analysis['recommendation']}")
        
        # Haber analizi
        if news_sentiment:
            print(f"\n📰 HABER ANALİZİ:")
            print(f"   Toplam Haber: {news_sentiment['total_news']}")
            print(f"   Sentiment: {news_sentiment['overall_sentiment']}")
            print(f"   Skor: {news_sentiment['sentiment_score']:.2f}")
    
    def _display_watchlist_summary(self, results):
        """Takip listesi özetini gösterir"""
        if not results:
            return
        
        print(f"\n📋 TAKİP LİSTESİ ÖZETİ")
        print("=" * 60)
        
        # Risk dağılımı
        risk_counts = {}
        opportunity_counts = {}
        
        for result in results:
            risk = result.get('risk_level', 'N/A')
            opportunity = result.get('opportunity_level', 'N/A')
            
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1
        
        print("⚠️ Risk Dağılımı:")
        for risk, count in risk_counts.items():
            print(f"   {risk}: {count} hisse")
        
        print("\n🎯 Fırsat Dağılımı:")
        for opp, count in opportunity_counts.items():
            print(f"   {opp}: {count} hisse")
        
        # En riskli ve en fırsatlı hisseler
        high_risk = [r for r in results if r.get('risk_level') == 'YÜKSEK']
        high_opportunity = [r for r in results if r.get('opportunity_level') == 'YÜKSEK']
        
        if high_risk:
            print(f"\n🚨 Yüksek Riskli Hisseler ({len(high_risk)}):")
            for stock in high_risk:
                print(f"   {stock['symbol']}: {stock['current_price']:.2f} TL")
        
        if high_opportunity:
            print(f"\n🚀 Yüksek Fırsatlı Hisseler ({len(high_opportunity)}):")
            for stock in high_opportunity:
                print(f"   {stock['symbol']}: {stock['current_price']:.2f} TL")
    
    def _create_charts(self, symbol, stock_data, technical_analysis, news_sentiment):
        """Grafikleri oluşturur"""
        try:
            # Fiyat grafiği
            price_chart = self.chart_generator.create_price_chart(stock_data)
            if price_chart:
                print(f"   📊 Fiyat grafiği: {price_chart}")
            
            # Teknik göstergeler grafiği
            tech_chart = self.chart_generator.create_technical_indicators_chart(stock_data, technical_analysis)
            if tech_chart:
                print(f"   🔧 Teknik göstergeler: {tech_chart}")
            
            # Sentiment grafiği
            if news_sentiment:
                sentiment_chart = self.chart_generator.create_sentiment_chart(news_sentiment)
                if sentiment_chart:
                    print(f"   📰 Sentiment grafiği: {sentiment_chart}")
        
        except Exception as e:
            print(f"   ❌ Grafik oluşturulurken hata: {str(e)}")
    
    def run_real_time_opportunity_analysis(self, market='both', min_decline=40):
        """
        Anlık fırsat analizi çalıştırır
        
        Args:
            market (str): 'bist', 'us', 'both'
            min_decline (float): Minimum düşüş yüzdesi
        """
        print(f"🔍 Anlık fırsat analizi başlatılıyor...")
        print(f"📊 Piyasa: {market.upper()}")
        print(f"📉 Minimum düşüş: %{min_decline}")
        print("=" * 60)
        
        try:
            # Fırsat analizi yap
            opportunities = self.opportunity_analyzer.get_real_time_opportunities(
                market=market, 
                min_decline=min_decline
            )
            
            if opportunities:
                print(f"\n✅ Toplam {len(opportunities)} fırsat bulundu!")
                print("\n🔥 En İyi Fırsatlar:")
                print("-" * 80)
                print(f"{'Sıra':<4} {'Sembol':<10} {'Piyasa':<6} {'Fiyat':<10} {'Değişim':<12} {'Skor':<8}")
                print("-" * 80)
                
                for i, opp in enumerate(opportunities[:10], 1):
                    print(f"{i:<4} {opp['symbol']:<10} {opp['market']:<6} "
                          f"{opp['current_price']:<10.2f} {opp['total_change']:<12.1f}% "
                          f"{opp['opportunity_score']:<8.1f}")
                
                # Takip listesine ekleme seçeneği
                print(f"\n📋 En iyi 5 fırsatı takip listesine eklemek ister misiniz? (y/n): ", end="")
                response = input().lower().strip()
                
                if response in ['y', 'yes', 'evet', 'e']:
                    result = self.opportunity_analyzer.add_to_watchlist_from_opportunities(opportunities, 5)
                    if result:
                        print(f"✅ {result['added_count']} hisse takip listesine eklendi!")
                        print("Eklenen hisseler:")
                        for stock in result['added_stocks']:
                            print(f"   • {stock['symbol']} ({stock['market']}) - Skor: {stock['opportunity_score']:.1f}")
                
                return opportunities
            else:
                print("❌ Belirtilen kriterlere uygun fırsat bulunamadı.")
                return []
                
        except Exception as e:
            print(f"❌ Fırsat analizi hatası: {str(e)}")
            return []
    
    def run_virtual_trading_demo(self):
        """Hayali alım-satım demo çalıştırır"""
        print("💰 Hayali Alım-Satım Demo Başlatılıyor...")
        print("=" * 60)
        
        # Kullanıcı bilgileri
        users = ['gokhan', 'yilmaz']
        
        for username in users:
            print(f"\n👤 {username.title()} Kullanıcısı:")
            balance = self.data_manager.get_user_balance(username)
            portfolio = self.data_manager.get_user_portfolio(username)
            
            print(f"   💰 Bakiye: {balance:,.2f} TL")
            print(f"   📊 Portföy: {len(portfolio)} hisse")
            
            if portfolio:
                total_value = sum([item['shares'] * item['avg_price'] for item in portfolio])
                print(f"   💎 Portföy Değeri: {total_value:,.2f} TL")
                
                for item in portfolio:
                    print(f"      • {item['symbol']}: {item['shares']} adet @ {item['avg_price']:.2f} TL")
        
        # Performans takibi
        print(f"\n📊 7 Günlük Performans Takibi:")
        print("-" * 60)
        
        for username in users:
            print(f"\n👤 {username.title()}:")
            performance = self.data_manager.get_performance_tracking(username)
            
            if performance:
                total_profit = sum([p['profit_loss'] for p in performance])
                total_investment = sum([p['initial_investment'] for p in performance])
                overall_return = (total_profit / total_investment * 100) if total_investment > 0 else 0
                
                print(f"   💰 Toplam Kar/Zarar: {total_profit:+,.2f} TL")
                print(f"   📈 Genel Getiri: {overall_return:+.2f}%")
                
                for perf in performance:
                    status = "🟢" if perf['profit_loss'] >= 0 else "🔴"
                    print(f"      {status} {perf['symbol']}: {perf['profit_loss']:+,.2f} TL ({perf['profit_loss_percent']:+.2f}%) - {perf['days_held']} gün")
            else:
                print("   📋 Henüz performans takibi bulunmuyor.")
    
    def demo_opportunity_to_trading_flow(self):
        """Fırsat analizinden alım işlemine demo akışı"""
        print("🔄 Fırsat Analizi → Takip Listesi → Alım İşlemi Demo Akışı")
        print("=" * 80)
        
        # 1. Fırsat analizi
        print("\n1️⃣ Fırsat Analizi Yapılıyor...")
        opportunities = self.run_real_time_opportunity_analysis(market='both', min_decline=30)
        
        if not opportunities:
            print("❌ Demo için fırsat bulunamadı.")
            return
        
        # 2. En iyi fırsatı seç
        best_opportunity = opportunities[0]
        print(f"\n2️⃣ En İyi Fırsat Seçildi: {best_opportunity['symbol']}")
        print(f"   📊 Piyasa: {best_opportunity['market']}")
        print(f"   💰 Fiyat: {best_opportunity['current_price']:.2f} {best_opportunity['currency']}")
        print(f"   📉 Değişim: {best_opportunity['total_change']:.1f}%")
        print(f"   🎯 Skor: {best_opportunity['opportunity_score']:.1f}/100")
        
        # 3. Takip listesine ekle
        print(f"\n3️⃣ Takip Listesine Ekleniyor...")
        success = self.data_manager.add_to_watchlist(
            best_opportunity['symbol'], 
            f"{best_opportunity['symbol']} - {best_opportunity['market']}"
        )
        
        if success:
            print(f"✅ {best_opportunity['symbol']} takip listesine eklendi!")
        else:
            print(f"⚠️ {best_opportunity['symbol']} zaten takip listesinde!")
        
        # 4. Gökhan kullanıcısı ile alım
        print(f"\n4️⃣ Gökhan Kullanıcısı ile Alım İşlemi...")
        symbol = best_opportunity['symbol']
        price = best_opportunity['current_price']
        quantity = 100  # 100 adet al
        
        success, message = self.data_manager.buy_stock("gokhan", symbol, quantity, price)
        
        if success:
            print(f"✅ Alım işlemi başarılı: {message}")
            print(f"   📊 {quantity} adet {symbol} @ {price:.2f} {best_opportunity['currency']}")
            
            # 5. Performans takibi başlat
            print(f"\n5️⃣ 7 Günlük Performans Takibi Başlatıldı")
            print(f"   📅 Takip başlangıcı: {datetime.now().strftime('%Y-%m-%d')}")
            print(f"   📈 7 gün sonra kar/zarar değerlendirmesi yapılacak")
        else:
            print(f"❌ Alım işlemi başarısız: {message}")
    
    def show_menu(self):
        """Ana menüyü gösterir"""
        print("\n📋 ANA MENÜ")
        print("=" * 40)
        print("1. 🔍 Anlık Fırsat Analizi")
        print("2. 💰 Hayali Alım-Satım Demo")
        print("3. 🔄 Fırsat → Takip → Alım Demo Akışı")
        print("4. 📊 Takip Listesi Analizi")
        print("5. 📈 Hisse Detay Analizi")
        print("6. 📋 Takip Listesi Yönetimi")
        print("7. 🚀 Web Uygulamasını Başlat")
        print("0. ❌ Çıkış")
        print("=" * 40)
    
    def run_interactive_mode(self):
        """Etkileşimli mod çalıştırır"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\nSeçiminizi yapın (0-7): ").strip()
                
                if choice == '0':
                    print("👋 Görüşürüz!")
                    break
                elif choice == '1':
                    market = input("Piyasa seçin (bist/us/both): ").strip() or 'both'
                    min_decline = float(input("Minimum düşüş (%) [40]: ").strip() or '40')
                    self.run_real_time_opportunity_analysis(market, min_decline)
                elif choice == '2':
                    self.run_virtual_trading_demo()
                elif choice == '3':
                    self.demo_opportunity_to_trading_flow()
                elif choice == '4':
                    days = int(input("Analiz günü [7]: ").strip() or '7')
                    self.analyze_watchlist(days)
                elif choice == '5':
                    symbol = input("Hisse sembolü: ").strip().upper()
                    if symbol:
                        days = int(input("Analiz günü [365]: ").strip() or '365')
                        self.analyze_stock(symbol, days)
                elif choice == '6':
                    self.show_watchlist_management()
                elif choice == '7':
                    print("🌐 Web uygulaması başlatılıyor...")
                    print("📱 Tarayıcınızda http://localhost:8501 adresini açın")
                    os.system("streamlit run web_app.py")
                else:
                    print("❌ Geçersiz seçim!")
                    
            except KeyboardInterrupt:
                print("\n👋 Görüşürüz!")
                break
            except Exception as e:
                print(f"❌ Hata: {str(e)}")
    
    def show_watchlist_management(self):
        """Takip listesi yönetimi"""
        print("\n📋 TAKİP LİSTESİ YÖNETİMİ")
        print("=" * 40)
        
        watchlist = self.data_manager.get_watchlist()
        
        if not watchlist:
            print("📋 Takip listeniz boş.")
            return
        
        print(f"📊 Toplam {len(watchlist)} hisse:")
        for i, item in enumerate(watchlist, 1):
            added_date = datetime.fromisoformat(item['added_date']).strftime('%d/%m/%Y')
            print(f"{i}. {item['symbol']} - {item['name']} (Eklenme: {added_date})")
        
        print("\nSeçenekler:")
        print("1. Hisse ekle")
        print("2. Hisse çıkar")
        print("3. Geri dön")
        
        choice = input("Seçiminiz: ").strip()
        
        if choice == '1':
            symbol = input("Hisse sembolü: ").strip().upper()
            name = input("Şirket adı (opsiyonel): ").strip()
            if symbol:
                success = self.data_manager.add_to_watchlist(symbol, name)
                if success:
                    print(f"✅ {symbol} takip listesine eklendi!")
                else:
                    print(f"⚠️ {symbol} zaten takip listesinde!")
        elif choice == '2':
            try:
                index = int(input("Çıkarılacak hisse numarası: ").strip()) - 1
                if 0 <= index < len(watchlist):
                    symbol = watchlist[index]['symbol']
                    success = self.data_manager.remove_from_watchlist(symbol)
                    if success:
                        print(f"✅ {symbol} takip listesinden çıkarıldı!")
                    else:
                        print(f"❌ {symbol} takip listesinde bulunamadı!")
                else:
                    print("❌ Geçersiz numara!")
            except ValueError:
                print("❌ Geçersiz numara!")


def main():
    """Ana fonksiyon"""
    try:
        app = StockAnalysisApp()
        app.run_interactive_mode()
    except Exception as e:
        print(f"❌ Uygulama başlatılırken hata oluştu: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 