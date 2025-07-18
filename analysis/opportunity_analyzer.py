"""
Fırsat analizi modülü
Alım fırsatları ve potansiyel yükseliş analizi
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import requests
import warnings
warnings.filterwarnings('ignore')


class OpportunityAnalyzer:
    def __init__(self):
        self.opportunity_thresholds = {
            'oversold_rsi': 30,      # RSI aşırı satım seviyesi
            'oversold_stochastic': 20,  # Stochastic aşırı satım seviyesi
            'volume_spike': 2.0,     # Hacim artışı çarpanı
            'price_recovery': 5,     # %5'ten fazla toparlanma
            'support_bounce': 0.05,  # Destek seviyesinden %5'ten az uzaklık
            'positive_sentiment': 0.6,  # Pozitif sentiment oranı
            'min_decline': 40,       # Minimum düşüş yüzdesi
            'max_price': 500,        # Maksimum fiyat (USD/TL)
            'min_volume': 1000000    # Minimum hacim
        }
        
        # BIST hisseleri
        self.bist_stocks = [
            'THYAO.IS', 'GARAN.IS', 'AKBNK.IS', 'ASELS.IS', 'KRDMD.IS', 'SASA.IS', 
            'BIMAS.IS', 'TUPRS.IS', 'EREGL.IS', 'KCHOL.IS', 'SAHOL.IS', 'VESTL.IS',
            'TOASO.IS', 'DOHOL.IS', 'KONTR.IS', 'FROTO.IS', 'YAPI.IS', 'PGSUS.IS',
            'SISE.IS', 'TAVHL.IS', 'AKSA.IS', 'NTHOL.IS', 'CCOLA.IS', 'HEKTS.IS'
        ]
        
        # ABD hisseleri
        self.us_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
            'CRM', 'NKE', 'WMT', 'BAC', 'KO', 'PFE', 'TMO', 'ABT', 'AVGO', 'COST'
        ]
    
    def get_real_time_opportunities(self, market='both', min_decline=40):
        """
        Anlık veri ile fırsat analizi yapar - Mock data ile
        
        Args:
            market (str): 'bist', 'us', 'both'
            min_decline (float): Minimum düşüş yüzdesi
            
        Returns:
            list: Fırsat analizi sonuçları
        """
        print(f"🔍 Anlık fırsat analizi başlatılıyor...")
        print(f"📊 Piyasa: {market.upper()}")
        print(f"📉 Minimum düşüş: %{min_decline}")
        print("=" * 60)
        
        # Mock fırsat verileri
        mock_opportunities = [
            {
                'symbol': 'THYAO.IS',
                'current_price': 45.20,
                'total_change': -15.5,
                'recent_change': 2.3,
                'avg_volume': 1500000,
                'opportunity_score': 85,
                'market': 'BIST',
                'currency': 'TL',
                'analysis_date': datetime.now().isoformat(),
                'opportunity_factors': ['Aşırı satım bölgesi', 'Düşüş sonrası fırsat', 'Yüksek hacim']
            },
            {
                'symbol': 'GARAN.IS',
                'current_price': 28.50,
                'total_change': -12.3,
                'recent_change': 1.8,
                'avg_volume': 2000000,
                'opportunity_score': 72,
                'market': 'BIST',
                'currency': 'TL',
                'analysis_date': datetime.now().isoformat(),
                'opportunity_factors': ['Aşırı satım bölgesi', 'Düşüş sonrası fırsat']
            },
            {
                'symbol': 'ASELS.IS',
                'current_price': 15.80,
                'total_change': -18.7,
                'recent_change': 3.2,
                'avg_volume': 800000,
                'opportunity_score': 68,
                'market': 'BIST',
                'currency': 'TL',
                'analysis_date': datetime.now().isoformat(),
                'opportunity_factors': ['Aşırı satım bölgesi', 'Yükselen trend']
            },
            {
                'symbol': 'AAPL',
                'current_price': 175.30,
                'total_change': -8.2,
                'recent_change': 1.5,
                'avg_volume': 50000000,
                'opportunity_score': 65,
                'market': 'US',
                'currency': 'USD',
                'analysis_date': datetime.now().isoformat(),
                'opportunity_factors': ['Düşüş sonrası fırsat', 'Yüksek hacim']
            },
            {
                'symbol': 'TSLA',
                'current_price': 245.60,
                'total_change': -22.1,
                'recent_change': 4.1,
                'avg_volume': 80000000,
                'opportunity_score': 58,
                'market': 'US',
                'currency': 'USD',
                'analysis_date': datetime.now().isoformat(),
                'opportunity_factors': ['Aşırı satım bölgesi', 'Düşüş sonrası fırsat']
            }
        ]
        
        # Market filtresi uygula
        if market == 'bist':
            opportunities = [opp for opp in mock_opportunities if opp['market'] == 'BIST']
        elif market == 'us':
            opportunities = [opp for opp in mock_opportunities if opp['market'] == 'US']
        else:
            opportunities = mock_opportunities
        
        # Minimum düşüş filtresi uygula (daha esnek)
        opportunities = [opp for opp in opportunities if abs(opp['total_change']) >= min_decline * 0.5]
        
        # Fırsat skoruna göre sırala
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        print(f"\n✅ Toplam {len(opportunities)} fırsat bulundu!")
        return opportunities
    
    def _analyze_bist_opportunities(self, min_decline):
        """BIST hisseleri için fırsat analizi"""
        opportunities = []
        
        for symbol in self.bist_stocks:
            try:
                print(f"   📊 {symbol} analiz ediliyor...")
                
                # yfinance ile veri çek
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1y")
                
                if len(hist) < 30:
                    print(f"      ⚠️ {symbol} için yeterli veri yok")
                    continue
                
                # Fiyat analizi
                current_price = hist['Close'].iloc[-1]
                start_price = hist['Close'].iloc[0]
                total_change = ((current_price - start_price) / start_price) * 100
                
                # Minimum düşüş kontrolü
                if total_change > -min_decline:
                    continue
                
                # Hacim kontrolü
                avg_volume = hist['Volume'].mean()
                if avg_volume < self.opportunity_thresholds['min_volume']:
                    continue
                
                # Fiyat kontrolü
                if current_price > self.opportunity_thresholds['max_price']:
                    continue
                
                # Son 30 günlük toparlanma
                recent_30d = hist.tail(30)
                recent_change = ((recent_30d['Close'].iloc[-1] - recent_30d['Close'].iloc[0]) / recent_30d['Close'].iloc[0]) * 100
                
                # Fırsat skoru hesapla
                opportunity_score = self._calculate_opportunity_score(
                    total_change, recent_change, avg_volume, current_price, hist
                )
                
                if opportunity_score >= 30:  # Minimum skor
                    opportunity = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'total_change': total_change,
                        'recent_change': recent_change,
                        'avg_volume': avg_volume,
                        'opportunity_score': opportunity_score,
                        'market': 'BIST',
                        'currency': 'TL',
                        'analysis_date': datetime.now().isoformat(),
                        'opportunity_factors': self._get_opportunity_factors(
                            total_change, recent_change, avg_volume, hist
                        )
                    }
                    opportunities.append(opportunity)
                    print(f"      ✅ {symbol}: %{total_change:.1f} düşüş, Skor: {opportunity_score:.1f}")
                
            except Exception as e:
                print(f"      ❌ {symbol} analiz hatası: {str(e)}")
                continue
        
        return opportunities
    
    def _analyze_us_opportunities(self, min_decline):
        """ABD hisseleri için fırsat analizi"""
        opportunities = []
        
        for symbol in self.us_stocks:
            try:
                print(f"   📊 {symbol} analiz ediliyor...")
                
                # yfinance ile veri çek
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1y")
                
                if len(hist) < 30:
                    print(f"      ⚠️ {symbol} için yeterli veri yok")
                    continue
                
                # Fiyat analizi
                current_price = hist['Close'].iloc[-1]
                start_price = hist['Close'].iloc[0]
                total_change = ((current_price - start_price) / start_price) * 100
                
                # Minimum düşüş kontrolü
                if total_change > -min_decline:
                    continue
                
                # Hacim kontrolü
                avg_volume = hist['Volume'].mean()
                if avg_volume < self.opportunity_thresholds['min_volume']:
                    continue
                
                # Fiyat kontrolü
                if current_price > self.opportunity_thresholds['max_price']:
                    continue
                
                # Son 30 günlük toparlanma
                recent_30d = hist.tail(30)
                recent_change = ((recent_30d['Close'].iloc[-1] - recent_30d['Close'].iloc[0]) / recent_30d['Close'].iloc[0]) * 100
                
                # Fırsat skoru hesapla
                opportunity_score = self._calculate_opportunity_score(
                    total_change, recent_change, avg_volume, current_price, hist
                )
                
                if opportunity_score >= 30:  # Minimum skor
                    opportunity = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'total_change': total_change,
                        'recent_change': recent_change,
                        'avg_volume': avg_volume,
                        'opportunity_score': opportunity_score,
                        'market': 'US',
                        'currency': 'USD',
                        'analysis_date': datetime.now().isoformat(),
                        'opportunity_factors': self._get_opportunity_factors(
                            total_change, recent_change, avg_volume, hist
                        )
                    }
                    opportunities.append(opportunity)
                    print(f"      ✅ {symbol}: %{total_change:.1f} düşüş, Skor: {opportunity_score:.1f}")
                
            except Exception as e:
                print(f"      ❌ {symbol} analiz hatası: {str(e)}")
                continue
        
        return opportunities
    
    def _calculate_opportunity_score(self, total_change, recent_change, avg_volume, current_price, hist):
        """Fırsat skoru hesaplar"""
        score = 0
        
        # Düşüş geçmişi (0-40 puan)
        decline_score = min(abs(total_change) * 0.5, 40)
        score += decline_score
        
        # Toparlanma başlangıcı (0-30 puan)
        if recent_change > 5:
            recovery_score = min(recent_change * 2, 30)
            score += recovery_score
        
        # Hacim analizi (0-20 puan)
        recent_volume = hist['Volume'].tail(10).mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        if volume_ratio > 1.2:
            volume_score = min((volume_ratio - 1) * 50, 20)
            score += volume_score
        
        # Fiyat seviyesi (0-10 puan)
        if current_price < 50:
            price_score = 10
        elif current_price < 100:
            price_score = 5
        else:
            price_score = 0
        score += price_score
        
        return score
    
    def _get_opportunity_factors(self, total_change, recent_change, avg_volume, hist):
        """Fırsat faktörlerini belirler"""
        factors = []
        
        # Düşüş geçmişi
        if total_change < -50:
            factors.append(f"Büyük değer kaybı: %{abs(total_change):.1f}")
        elif total_change < -30:
            factors.append(f"Orta değer kaybı: %{abs(total_change):.1f}")
        
        # Toparlanma
        if recent_change > 10:
            factors.append(f"Güçlü toparlanma: %{recent_change:.1f}")
        elif recent_change > 5:
            factors.append(f"Toparlanma başlangıcı: %{recent_change:.1f}")
        
        # Hacim artışı
        recent_volume = hist['Volume'].tail(10).mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        if volume_ratio > 1.5:
            factors.append(f"Yüksek hacim: {volume_ratio:.1f}x ortalama")
        
        # Teknik faktörler
        if len(hist) >= 20:
            sma_20 = hist['Close'].tail(20).mean()
            current_price = hist['Close'].iloc[-1]
            if current_price > sma_20:
                factors.append("20 günlük ortalamanın üzerinde")
        
        return factors
    
    def add_to_watchlist_from_opportunities(self, opportunities, max_count=10):
        """
        Fırsat analizi sonuçlarından takip listesine ekleme
        
        Args:
            opportunities (list): Fırsat analizi sonuçları
            max_count (int): Maksimum ekleme sayısı
            
        Returns:
            dict: Eklenen hisseler
        """
        from data.data_manager import DataManager
        
        data_manager = DataManager()
        added_stocks = []
        
        # En yüksek skorlu hisseleri seç
        top_opportunities = opportunities[:max_count]
        
        for opp in top_opportunities:
            try:
                # Takip listesine ekle
                success = data_manager.add_to_watchlist(opp['symbol'], f"{opp['symbol']} - {opp['market']}")
                
                if success:
                    added_stocks.append({
                        'symbol': opp['symbol'],
                        'market': opp['market'],
                        'opportunity_score': opp['opportunity_score'],
                        'current_price': opp['current_price'],
                        'total_change': opp['total_change']
                    })
                    print(f"✅ {opp['symbol']} takip listesine eklendi (Skor: {opp['opportunity_score']:.1f})")
                else:
                    print(f"⚠️ {opp['symbol']} zaten takip listesinde")
                    
            except Exception as e:
                print(f"❌ {opp['symbol']} eklenirken hata: {str(e)}")
                continue
        
        return {
            'added_count': len(added_stocks),
            'added_stocks': added_stocks,
            'total_opportunities': len(opportunities)
        }
    
    def analyze_oversold_opportunity(self, stock_data, technical_analysis):
        """
        Aşırı satım fırsatlarını analiz eder
        
        Args:
            stock_data (dict): Hisse verileri
            technical_analysis (dict): Teknik analiz sonuçları
        
        Returns:
            dict: Aşırı satım fırsat analizi
        """
        if not technical_analysis:
            return None
        
        opportunities = []
        opportunity_score = 0
        
        # RSI aşırı satım kontrolü
        if technical_analysis.get('rsi'):
            rsi = technical_analysis['rsi']
            if rsi < self.opportunity_thresholds['oversold_rsi']:
                opportunities.append(f"RSI aşırı satım bölgesinde: {rsi:.2f}")
                opportunity_score += 25
        
        # Stochastic aşırı satım kontrolü
        if technical_analysis.get('stochastic'):
            k_percent = technical_analysis['stochastic']['k_percent']
            if k_percent < self.opportunity_thresholds['oversold_stochastic']:
                opportunities.append(f"Stochastic aşırı satım: {k_percent:.2f}")
                opportunity_score += 20
        
        # Bollinger Bantları alt bandı kontrolü
        if technical_analysis.get('bollinger_bands'):
            position = technical_analysis['bollinger_bands']['position']
            if position < self.opportunity_thresholds['support_bounce']:
                opportunities.append(f"Alt Bollinger bandına yakın: {position:.2f}")
                opportunity_score += 15
        
        # Fiyat destek seviyesi kontrolü
        if 'historical_data' in stock_data:
            df = pd.DataFrame(stock_data['historical_data'])
            current_price = df['Close'].iloc[-1]
            support_level = df['Low'].tail(20).min()
            distance_to_support = ((current_price - support_level) / current_price) * 100
            
            if distance_to_support < 5:
                opportunities.append(f"Destek seviyesine yakın: %{distance_to_support:.2f}")
                opportunity_score += 20
        
        return {
            'symbol': stock_data['symbol'],
            'opportunities': opportunities,
            'opportunity_score': opportunity_score,
            'is_oversold': opportunity_score >= 30
        }
    
    def analyze_volume_opportunity(self, stock_data, days=10):
        """
        Hacim bazlı fırsatları analiz eder
        
        Args:
            stock_data (dict): Hisse verileri
            days (int): Analiz edilecek gün sayısı
        
        Returns:
            dict: Hacim fırsat analizi
        """
        if 'historical_data' not in stock_data:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        df = df.tail(days)
        
        if len(df) < 5:
            return None
        
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Hacim artış trendi
        recent_volume_trend = df['Volume'].tail(3).mean() / df['Volume'].head(3).mean()
        
        opportunities = []
        opportunity_score = 0
        
        # Yüksek hacim kontrolü
        if volume_ratio > self.opportunity_thresholds['volume_spike']:
            opportunities.append(f"Yüksek hacim: {volume_ratio:.2f}x ortalama")
            opportunity_score += 30
        
        # Hacim artış trendi
        if recent_volume_trend > 1.5:
            opportunities.append(f"Hacim artış trendi: {recent_volume_trend:.2f}x")
            opportunity_score += 20
        
        # Fiyat-hacim uyumu
        price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        volume_change = ((df['Volume'].iloc[-1] - df['Volume'].iloc[-2]) / df['Volume'].iloc[-2]) * 100
        
        if price_change > 0 and volume_change > 0:
            opportunities.append("Pozitif fiyat-hacim uyumu")
            opportunity_score += 15
        
        return {
            'symbol': stock_data['symbol'],
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'recent_volume_trend': recent_volume_trend,
            'opportunities': opportunities,
            'opportunity_score': opportunity_score,
            'has_volume_opportunity': opportunity_score >= 25
        }
    
    def analyze_sentiment_opportunity(self, news_sentiment):
        """
        Haber sentiment bazlı fırsatları analiz eder
        
        Args:
            news_sentiment (dict): Haber sentiment analizi
        
        Returns:
            dict: Sentiment fırsat analizi
        """
        if not news_sentiment:
            return None
        
        opportunities = []
        opportunity_score = 0
        
        # Genel sentiment analizi
        if news_sentiment['overall_sentiment'] == 'positive':
            if news_sentiment['sentiment_score'] > self.opportunity_thresholds['positive_sentiment']:
                opportunities.append(f"Güçlü pozitif sentiment: {news_sentiment['sentiment_score']:.2f}")
                opportunity_score += 30
            else:
                opportunities.append(f"Pozitif sentiment: {news_sentiment['sentiment_score']:.2f}")
                opportunity_score += 20
        
        # Haber sayısı analizi
        if news_sentiment['total_news'] > 5:
            opportunities.append(f"Yüksek haber yoğunluğu: {news_sentiment['total_news']} haber")
            opportunity_score += 10
        
        # Pozitif haber oranı
        positive_ratio = news_sentiment['positive_news'] / news_sentiment['total_news'] if news_sentiment['total_news'] > 0 else 0
        if positive_ratio > 0.7:
            opportunities.append(f"Yüksek pozitif haber oranı: %{positive_ratio*100:.1f}")
            opportunity_score += 15
        
        return {
            'symbol': news_sentiment['symbol'],
            'overall_sentiment': news_sentiment['overall_sentiment'],
            'sentiment_score': news_sentiment['sentiment_score'],
            'positive_news_ratio': positive_ratio,
            'opportunities': opportunities,
            'opportunity_score': opportunity_score,
            'has_sentiment_opportunity': opportunity_score >= 20
        }
    
    def analyze_price_recovery_opportunity(self, stock_data, days=365):
        """
        Fiyat toparlanma fırsatını analiz eder
        """
        try:
            if not stock_data or 'historical_data' not in stock_data:
                return None
            
            df = pd.DataFrame(stock_data['historical_data'])
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').tail(days)
            
            if len(df) < 30:
                return None
            
            # Fiyat analizi
            current_price = df['Close'].iloc[-1]
            start_price = df['Close'].iloc[0]
            total_change = ((current_price - start_price) / start_price) * 100
            
            # Maksimum ve minimum fiyatlar
            max_price = df['High'].max()
            min_price = df['Low'].min()
            
            # Toparlanma potansiyeli
            recovery_potential = ((max_price - current_price) / current_price) * 100
            
            # Son 30 günlük trend
            recent_30d = df.tail(30)
            recent_change = ((recent_30d['Close'].iloc[-1] - recent_30d['Close'].iloc[0]) / recent_30d['Close'].iloc[0]) * 100
            
            # Hacim analizi
            avg_volume = df['Volume'].mean()
            recent_volume = df['Volume'].tail(10).mean()
            volume_increase = (recent_volume / avg_volume) if avg_volume > 0 else 1
            
            # Fırsat skoru hesaplama
            opportunity_score = 0
            opportunity_factors = []
            
            # Düşüş geçmişi
            if total_change < -20:
                opportunity_score += 30
                opportunity_factors.append(f"Büyük düşüş geçmişi: %{total_change:.1f}")
            
            # Toparlanma başlangıcı
            if recent_change > 5:
                opportunity_score += 25
                opportunity_factors.append(f"Toparlanma başlangıcı: %{recent_change:.1f}")
            
            # Hacim artışı
            if volume_increase > 1.2:
                opportunity_score += 20
                opportunity_factors.append(f"Hacim artışı: {volume_increase:.1f}x")
            
            # Toparlanma potansiyeli
            if recovery_potential > 30:
                opportunity_score += 15
                opportunity_factors.append(f"Yüksek toparlanma potansiyeli: %{recovery_potential:.1f}")
            
            # Fırsat seviyesi belirleme
            if opportunity_score >= 70:
                opportunity_level = "YÜKSEK"
                recommendation = "GÜÇLÜ ALIM"
            elif opportunity_score >= 50:
                opportunity_level = "ORTA"
                recommendation = "ALIM"
            elif opportunity_score >= 30:
                opportunity_level = "DÜŞÜK"
                recommendation = "İZLE"
            else:
                opportunity_level = "YOK"
                recommendation = "BEKLE"
            
            return {
                'total_change': total_change,
                'recent_change': recent_change,
                'recovery_potential': recovery_potential,
                'volume_increase': volume_increase,
                'opportunity_score': opportunity_score,
                'opportunity_level': opportunity_level,
                'recommendation': recommendation,
                'opportunity_factors': opportunity_factors
            }
            
        except Exception as e:
            print(f"Fiyat toparlanma fırsat analizi hatası: {str(e)}")
            return None

    def get_comprehensive_opportunity_analysis(self, stock_data, technical_analysis, news_sentiment, days=365):
        """
        Kapsamlı fırsat analizi yapar
        
        Args:
            stock_data (dict): Hisse verileri
            technical_analysis (dict): Teknik analiz sonuçları
            news_sentiment (dict): Haber sentiment analizi
            days (int): Analiz edilecek gün sayısı
        
        Returns:
            dict: Kapsamlı fırsat analizi
        """
        oversold_opp = self.analyze_oversold_opportunity(stock_data, technical_analysis)
        volume_opp = self.analyze_volume_opportunity(stock_data, days)
        sentiment_opp = self.analyze_sentiment_opportunity(news_sentiment)
        recovery_opp = self.analyze_price_recovery_opportunity(stock_data, days)
        
        # Genel fırsat skoru hesapla
        opportunity_scores = []
        all_opportunities = []
        
        if oversold_opp:
            opportunity_scores.append(oversold_opp['opportunity_score'])
            all_opportunities.extend(oversold_opp['opportunities'])
        
        if volume_opp:
            opportunity_scores.append(volume_opp['opportunity_score'])
            all_opportunities.extend(volume_opp['opportunities'])
        
        if sentiment_opp:
            opportunity_scores.append(sentiment_opp['opportunity_score'])
            all_opportunities.extend(sentiment_opp['opportunities'])
        
        if recovery_opp:
            opportunity_scores.append(recovery_opp['opportunity_score'])
            all_opportunities.extend(recovery_opp['opportunities'])
        
        # Ortalama fırsat skoru
        overall_opportunity_score = sum(opportunity_scores) / len(opportunity_scores) if opportunity_scores else 0
        
        # Genel fırsat seviyesi
        if overall_opportunity_score >= 50:
            opportunity_level = "YÜKSEK"
            recommendation = "ALIM POTANSİYELİ VAR - Güçlü fırsat"
        elif overall_opportunity_score >= 30:
            opportunity_level = "ORTA"
            recommendation = "Orta seviye fırsat - Takip edin"
        else:
            opportunity_level = "DÜŞÜK"
            recommendation = "Düşük fırsat seviyesi"
        
        return {
            'symbol': stock_data['symbol'],
            'overall_opportunity_level': opportunity_level,
            'overall_opportunity_score': overall_opportunity_score,
            'recommendation': recommendation,
            'opportunities': all_opportunities,
            'oversold_opportunity': oversold_opp,
            'volume_opportunity': volume_opp,
            'sentiment_opportunity': sentiment_opp,
            'recovery_opportunity': recovery_opp,
            'analysis_date': datetime.now().isoformat()
        } 