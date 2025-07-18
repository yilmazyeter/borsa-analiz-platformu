"""
Haber Sentiment Analizi Modülü
Haber metinlerini analiz ederek duyarlılık skorları hesaplar
"""

import re
import numpy as np
from datetime import datetime

class SentimentAnalyzer:
    """Haber sentiment analizi sınıfı"""
    
    def __init__(self):
        # Pozitif ve negatif kelime listeleri
        self.positive_words = {
            'yükseliş', 'artış', 'büyüme', 'kazanç', 'kâr', 'olumlu', 'güçlü',
            'başarılı', 'iyi', 'mükemmel', 'harika', 'süper', 'arttı', 'yükseldi',
            'kazandı', 'başardı', 'gelişti', 'iyileşti', 'güçlendi', 'büyüdü',
            'rise', 'increase', 'growth', 'profit', 'gain', 'positive', 'strong',
            'successful', 'good', 'excellent', 'great', 'super', 'increased', 'rose',
            'gained', 'achieved', 'improved', 'strengthened', 'grew'
        }
        
        self.negative_words = {
            'düşüş', 'azalış', 'kayıp', 'zarar', 'olumsuz', 'zayıf', 'başarısız',
            'kötü', 'korkunç', 'berbat', 'düştü', 'azaldı', 'kaybetti', 'başarısız',
            'bozuldu', 'kötüleşti', 'zayıfladı', 'küçüldü', 'çöktü', 'iflas',
            'fall', 'decrease', 'loss', 'negative', 'weak', 'failed', 'bad',
            'terrible', 'awful', 'fell', 'decreased', 'lost', 'failed', 'worsened',
            'weakened', 'shrunk', 'crashed', 'bankruptcy'
        }
        
        # Finansal terimler ve ağırlıkları
        self.financial_terms = {
            'hisse': 1.5, 'borsa': 1.3, 'piyasa': 1.2, 'yatırım': 1.4,
            'stock': 1.5, 'market': 1.3, 'investment': 1.4, 'trading': 1.2,
            'fiyat': 1.6, 'değer': 1.5, 'price': 1.6, 'value': 1.5,
            'kâr': 2.0, 'zarar': -2.0, 'profit': 2.0, 'loss': -2.0,
            'büyüme': 1.8, 'küçülme': -1.8, 'growth': 1.8, 'shrink': -1.8
        }
    
    def analyze_text(self, text):
        """
        Metin sentiment analizi yapar
        
        Args:
            text (str): Analiz edilecek metin
            
        Returns:
            dict: Sentiment analiz sonuçları
        """
        try:
            if not text or len(text.strip()) < 10:
                return self._default_sentiment()
            
            # Metni temizle
            clean_text = self._clean_text(text.lower())
            
            # Kelime sayılarını hesapla
            words = clean_text.split()
            total_words = len(words)
            
            if total_words == 0:
                return self._default_sentiment()
            
            # Pozitif ve negatif kelime sayıları
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            
            # Finansal terim ağırlıkları
            financial_score = 0
            for term, weight in self.financial_terms.items():
                if term in clean_text:
                    financial_score += weight
            
            # Sentiment skoru hesapla
            sentiment_score = (positive_count - negative_count) / total_words
            sentiment_score += financial_score / total_words
            
            # Güven skoru
            confidence = min(0.95, (positive_count + negative_count) / total_words * 10)
            
            # Sentiment kategorisi
            if sentiment_score > 0.1:
                sentiment = 'positive'
                sentiment_label = 'Pozitif'
            elif sentiment_score < -0.1:
                sentiment = 'negative'
                sentiment_label = 'Negatif'
            else:
                sentiment = 'neutral'
                sentiment_label = 'Nötr'
            
            # Finansal etki seviyesi
            if abs(financial_score) > 3:
                financial_impact = 'Yüksek'
            elif abs(financial_score) > 1:
                financial_impact = 'Orta'
            else:
                financial_impact = 'Düşük'
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment': sentiment,
                'sentiment_label': sentiment_label,
                'confidence': round(confidence, 2),
                'positive_words': positive_count,
                'negative_words': negative_count,
                'financial_score': round(financial_score, 2),
                'financial_impact': financial_impact,
                'total_words': total_words,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Sentiment analizi hatası: {str(e)}")
            return self._default_sentiment()
    
    def analyze_news_batch(self, news_list):
        """
        Haber listesi için toplu sentiment analizi
        
        Args:
            news_list (list): Haber listesi
            
        Returns:
            list: Analiz edilmiş haber listesi
        """
        results = []
        
        for news in news_list:
            # Haber metnini birleştir
            text = f"{news.get('title', '')} {news.get('content', '')}"
            
            # Sentiment analizi yap
            sentiment_result = self.analyze_text(text)
            
            # Sonuçları birleştir
            news_with_sentiment = {**news, **sentiment_result}
            results.append(news_with_sentiment)
        
        return results
    
    def get_sentiment_summary(self, sentiment_results):
        """
        Sentiment sonuçlarından özet çıkarır
        
        Args:
            sentiment_results (list): Sentiment analiz sonuçları
            
        Returns:
            dict: Sentiment özeti
        """
        if not sentiment_results:
            return self._default_summary()
        
        total_news = len(sentiment_results)
        positive_count = sum(1 for r in sentiment_results if r['sentiment'] == 'positive')
        negative_count = sum(1 for r in sentiment_results if r['sentiment'] == 'negative')
        neutral_count = total_news - positive_count - negative_count
        
        avg_confidence = np.mean([r['confidence'] for r in sentiment_results])
        avg_sentiment = np.mean([r['sentiment_score'] for r in sentiment_results])
        
        # Piyasa sentiment'i
        if avg_sentiment > 0.1:
            market_sentiment = 'Pozitif'
        elif avg_sentiment < -0.1:
            market_sentiment = 'Negatif'
        else:
            market_sentiment = 'Nötr'
        
        return {
            'total_news': total_news,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': (positive_count / total_news) * 100 if total_news > 0 else 0,
            'negative_ratio': (negative_count / total_news) * 100 if total_news > 0 else 0,
            'neutral_ratio': (neutral_count / total_news) * 100 if total_news > 0 else 0,
            'avg_confidence': avg_confidence,
            'avg_sentiment_score': round(avg_sentiment, 3),
            'market_sentiment': market_sentiment
        }
    
    def _clean_text(self, text):
        """Metni temizler"""
        # Özel karakterleri kaldır
        text = re.sub(r'[^\w\s]', ' ', text)
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _default_sentiment(self):
        """Varsayılan sentiment sonucu"""
        return {
            'sentiment_score': 0.0,
            'sentiment': 'neutral',
            'sentiment_label': 'Nötr',
            'confidence': 0.5,
            'positive_words': 0,
            'negative_words': 0,
            'financial_score': 0.0,
            'financial_impact': 'Düşük',
            'total_words': 0,
            'analysis_date': datetime.now().isoformat()
        }
    
    def _default_summary(self):
        """Varsayılan özet sonucu"""
        return {
            'total_news': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_ratio': 0,
            'negative_ratio': 0,
            'neutral_ratio': 0,
            'avg_confidence': 0.5,
            'avg_sentiment_score': 0.0,
            'market_sentiment': 'Nötr'
        } 