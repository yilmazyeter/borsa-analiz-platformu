"""
NLP Asistan Modülü
Doğal dil ile kullanıcı sorularını yanıtlar
"""

import re
from datetime import datetime, timedelta

class NLPAssistant:
    """Doğal dil işleme asistanı"""
    
    def __init__(self):
        self.question_patterns = {
            'price_prediction': [
                r'(fiyat|price).*(tahmin|prediction|forecast)',
                r'(ne kadar|kaç|how much).*(olacak|will be)',
                r'(yükselir|düşer|rise|fall|up|down)',
                r'(al|sat|buy|sell).*(öneri|recommendation)'
            ],
            'performance_analysis': [
                r'(performans|performance).*(analiz|analysis)',
                r'(en iyi|best).*(hisse|stock)',
                r'(en kötü|worst).*(hisse|stock)',
                r'(kazanç|gain|profit).*(kayıp|loss)'
            ],
            'trend_analysis': [
                r'(trend|yön|direction).*(analiz|analysis)',
                r'(yükseliş|düşüş|rise|fall|up|down)',
                r'(momentum|momentum)',
                r'(destek|direnç|support|resistance)'
            ],
            'portfolio_advice': [
                r'(portföy|portfolio).*(öneri|advice|suggestion)',
                r'(hangi|which).*(hisse|stock).*(al|buy)',
                r'(sat|sell).*(hisse|stock)',
                r'(risk|risk).*(analiz|analysis)'
            ],
            'market_overview': [
                r'(piyasa|market).*(durum|overview|summary)',
                r'(borsa|stock market).*(nasıl|how)',
                r'(güncel|current).*(durum|situation)',
                r'(haber|news).*(etki|impact)'
            ]
        }
        
        self.response_templates = {
            'price_prediction': [
                "📈 {symbol} için fiyat tahmini: Güncel fiyat ${current_price}, {prediction_days} günlük tahmin ${predicted_price} ({change_percent}%)",
                "🔮 {symbol} fiyat analizi: Trend {trend_direction}, güven skoru %{confidence}",
                "💡 {symbol} önerisi: {recommendation} - {reason}"
            ],
            'performance_analysis': [
                "📊 Performans analizi: {symbol} son {period} günde {performance}% {direction}",
                "🏆 En iyi performans: {top_stocks}",
                "⚠️ En kötü performans: {worst_stocks}"
            ],
            'trend_analysis': [
                "📈 Trend analizi: {symbol} {trend_direction} trendinde, güç: {strength}",
                "🎯 Destek/Direnç: Destek ${support}, Direnç ${resistance}",
                "📊 Momentum: {momentum_direction}, güç: {momentum_strength}"
            ],
            'portfolio_advice': [
                "💼 Portföy önerisi: {advice}",
                "📈 Alım önerisi: {buy_recommendations}",
                "📉 Satış önerisi: {sell_recommendations}",
                "⚠️ Risk analizi: {risk_level} risk seviyesi"
            ],
            'market_overview': [
                "🌍 Piyasa durumu: {market_sentiment}",
                "📰 Haber etkisi: {news_impact}",
                "📊 Genel trend: {overall_trend}"
            ]
        }
    
    def process_question(self, question, context_data):
        """
        Kullanıcı sorusunu işler ve yanıt döndürür
        
        Args:
            question (str): Kullanıcı sorusu
            context_data (dict): Bağlam verileri (hisse verileri, portföy vb.)
            
        Returns:
            dict: Yanıt ve güven skoru
        """
        try:
            if not question or len(question.strip()) < 5:
                return self._default_response()
            
            # Soruyu temizle ve küçük harfe çevir
            clean_question = question.lower().strip()
            
            # Soru türünü belirle
            question_type = self._classify_question(clean_question)
            
            # Yanıt oluştur
            response = self._generate_response(question_type, clean_question, context_data)
            
            # Güven skoru hesapla
            confidence = self._calculate_confidence(question_type, clean_question)
            
            # Önerilen sorular
            suggestions = self._get_suggestions(question_type)
            
            return {
                'response': response,
                'confidence': confidence,
                'question_type': question_type,
                'suggestions': suggestions,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"NLP işleme hatası: {str(e)}")
            return self._default_response()
    
    def _classify_question(self, question):
        """Soru türünü sınıflandırır"""
        for question_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    return question_type
        
        return 'general'
    
    def _generate_response(self, question_type, question, context_data):
        """Yanıt oluşturur"""
        try:
            if question_type == 'price_prediction':
                return self._generate_price_response(question, context_data)
            elif question_type == 'performance_analysis':
                return self._generate_performance_response(question, context_data)
            elif question_type == 'trend_analysis':
                return self._generate_trend_response(question, context_data)
            elif question_type == 'portfolio_advice':
                return self._generate_portfolio_response(question, context_data)
            elif question_type == 'market_overview':
                return self._generate_market_response(question, context_data)
            else:
                return self._generate_general_response(question, context_data)
                
        except Exception as e:
            return f"Üzgünüm, bu soruya yanıt veremiyorum. Hata: {str(e)}"
    
    def _generate_price_response(self, question, context_data):
        """Fiyat tahmini yanıtı"""
        # Hisse sembolünü çıkar
        symbols = self._extract_symbols(question)
        
        if not symbols:
            return "Hangi hisse için fiyat tahmini istiyorsunuz? Lütfen hisse sembolünü belirtin."
        
        symbol = symbols[0]
        stock_data = context_data.get('stock_data', {}).get(symbol)
        
        if not stock_data:
            return f"{symbol} için veri bulunamadı. Lütfen geçerli bir hisse sembolü girin."
        
        current_price = stock_data.get('current_price', 0)
        
        # Basit tahmin
        prediction_days = 7
        predicted_price = current_price * 1.05  # %5 artış varsayımı
        change_percent = 5.0
        
        return f"📈 {symbol} için fiyat tahmini: Güncel fiyat ${current_price:.2f}, {prediction_days} günlük tahmin ${predicted_price:.2f} ({change_percent:+.1f}%)"
    
    def _generate_performance_response(self, question, context_data):
        """Performans analizi yanıtı"""
        stock_data = context_data.get('stock_data', {})
        
        if not stock_data:
            return "Performans analizi için hisse verisi bulunamadı."
        
        # En iyi ve en kötü performanslı hisseleri bul
        performances = []
        for symbol, data in stock_data.items():
            if data and 'change_365d' in data:
                performances.append((symbol, data['change_365d']))
        
        if not performances:
            return "Performans verisi bulunamadı."
        
        # Sırala
        performances.sort(key=lambda x: x[1], reverse=True)
        
        top_stocks = ", ".join([f"{symbol} ({change:+.1f}%)" for symbol, change in performances[:3]])
        worst_stocks = ", ".join([f"{symbol} ({change:+.1f}%)" for symbol, change in performances[-3:]])
        
        return f"📊 Performans analizi:\n🏆 En iyi: {top_stocks}\n⚠️ En kötü: {worst_stocks}"
    
    def _generate_trend_response(self, question, context_data):
        """Trend analizi yanıtı"""
        symbols = self._extract_symbols(question)
        
        if not symbols:
            return "Hangi hisse için trend analizi istiyorsunuz?"
        
        symbol = symbols[0]
        stock_data = context_data.get('stock_data', {}).get(symbol)
        
        if not stock_data:
            return f"{symbol} için trend verisi bulunamadı."
        
        change_365d = stock_data.get('change_365d', 0)
        
        if change_365d > 5:
            trend_direction = "yükseliş"
            strength = "güçlü"
        elif change_365d > 0:
            trend_direction = "yükseliş"
            strength = "zayıf"
        elif change_365d < -5:
            trend_direction = "düşüş"
            strength = "güçlü"
        else:
            trend_direction = "düşüş"
            strength = "zayıf"
        
        return f"📈 {symbol} trend analizi: {trend_direction} trendinde, güç: {strength} ({change_365d:+.1f}%)"
    
    def _generate_portfolio_response(self, question, context_data):
        """Portföy önerisi yanıtı"""
        portfolio = context_data.get('portfolio', [])
        
        if not portfolio:
            return "Portföy verisi bulunamadı. Önce hisse alımı yapın."
        
        # Basit portföy önerisi
        total_stocks = len(portfolio)
        
        if total_stocks < 3:
            advice = "Portföyünüzü çeşitlendirmenizi öneririm. En az 3-5 farklı hisse alın."
        elif total_stocks < 10:
            advice = "Portföyünüz iyi çeşitlendirilmiş. Risk yönetimi için stop-loss kullanın."
        else:
            advice = "Portföyünüz çok çeşitlendirilmiş. Performans takibi yapın."
        
        return f"💼 Portföy önerisi: {advice} (Toplam {total_stocks} hisse)"
    
    def _generate_market_response(self, question, context_data):
        """Piyasa durumu yanıtı"""
        news_sentiment = context_data.get('news_sentiment', {})
        
        sentiment = news_sentiment.get('category', 'Nötr')
        
        if sentiment == 'Pozitif':
            market_sentiment = "Pozitif"
            overall_trend = "Yükseliş eğiliminde"
        elif sentiment == 'Negatif':
            market_sentiment = "Negatif"
            overall_trend = "Düşüş eğiliminde"
        else:
            market_sentiment = "Nötr"
            overall_trend = "Yatay hareket"
        
        return f"🌍 Piyasa durumu: {market_sentiment}\n📊 Genel trend: {overall_trend}"
    
    def _generate_general_response(self, question, context_data):
        """Genel yanıt"""
        return "Bu soruya yanıt verebilmek için daha fazla bilgiye ihtiyacım var. Lütfen sorunuzu daha spesifik hale getirin."
    
    def _extract_symbols(self, question):
        """Soru içinden hisse sembollerini çıkarır"""
        # Basit sembol tespiti (büyük harfler)
        symbols = re.findall(r'\b[A-Z]{2,5}\b', question.upper())
        return symbols
    
    def _calculate_confidence(self, question_type, question):
        """Güven skoru hesaplar"""
        base_confidence = {
            'price_prediction': 75,
            'performance_analysis': 80,
            'trend_analysis': 70,
            'portfolio_advice': 65,
            'market_overview': 60,
            'general': 30
        }
        
        confidence = base_confidence.get(question_type, 50)
        
        # Soru uzunluğuna göre düzeltme
        if len(question) > 50:
            confidence += 10
        elif len(question) < 10:
            confidence -= 20
        
        return min(max(confidence, 20), 95)
    
    def _get_suggestions(self, question_type):
        """Önerilen sorular"""
        suggestions = {
            'price_prediction': [
                "AAPL fiyatı ne kadar olacak?",
                "Tesla hissesi yükselir mi?",
                "Hangi hisseyi almalıyım?"
            ],
            'performance_analysis': [
                "En iyi performans gösteren hisseler hangileri?",
                "Son 30 günde en çok değer kazanan hisseler?",
                "Hangi hisseler en çok düştü?"
            ],
            'trend_analysis': [
                "AAPL trend analizi nasıl?",
                "Hangi hisseler yükseliş trendinde?",
                "Destek ve direnç seviyeleri neler?"
            ],
            'portfolio_advice': [
                "Portföyümü nasıl optimize edebilirim?",
                "Hangi hisseyi satmalıyım?",
                "Risk analizi yapabilir misin?"
            ],
            'market_overview': [
                "Piyasa durumu nasıl?",
                "Güncel haberler piyasayı nasıl etkiliyor?",
                "Genel trend nedir?"
            ]
        }
        
        return suggestions.get(question_type, [
            "Fiyat tahmini yapabilir misin?",
            "Hangi hisseyi almalıyım?",
            "Portföy önerisi verir misin?"
        ])
    
    def _default_response(self):
        """Varsayılan yanıt"""
        return {
            'response': "Üzgünüm, sorunuzu anlayamadım. Lütfen daha açık bir şekilde sorun.",
            'confidence': 20,
            'question_type': 'unknown',
            'suggestions': [
                "Fiyat tahmini yapabilir misin?",
                "Hangi hisseyi almalıyım?",
                "Portföy önerisi verir misin?"
            ],
            'processed_at': datetime.now().isoformat()
        } 