"""
Haber Analiz Modülü - Sentiment Analizi ve Haber Etkisi Hesaplama
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random

class NewsAnalyzer:
    """Haber sentiment analizi ve etki hesaplama sınıfı"""
    
    def __init__(self):
        # Sentiment anahtar kelimeleri
        self.positive_words = [
            'yükseliş', 'artış', 'büyüme', 'kazanç', 'kar', 'olumlu', 'güçlü',
            'başarı', 'rekor', 'yüksek', 'iyi', 'mükemmel', 'harika', 'süper',
            'rise', 'gain', 'profit', 'positive', 'strong', 'success', 'record',
            'high', 'good', 'excellent', 'great', 'super', 'bullish', 'rally'
        ]
        
        self.negative_words = [
            'düşüş', 'kayıp', 'zarar', 'olumsuz', 'zayıf', 'başarısız', 'düşük',
            'kötü', 'kriz', 'risk', 'tehlike', 'kaygı', 'endişe', 'panik',
            'fall', 'loss', 'negative', 'weak', 'failure', 'low', 'bad',
            'crisis', 'risk', 'danger', 'worry', 'concern', 'panic', 'bearish'
        ]
        
        # Sektör anahtar kelimeleri
        self.sector_keywords = {
            'teknoloji': ['teknoloji', 'yazılım', 'donanım', 'internet', 'dijital', 'AI', 'yapay zeka'],
            'finans': ['banka', 'finans', 'kredi', 'yatırım', 'borsa', 'hisse'],
            'enerji': ['petrol', 'gaz', 'elektrik', 'enerji', 'yenilenebilir'],
            'sağlık': ['ilaç', 'sağlık', 'hastane', 'tedavi', 'medikal'],
            'otomotiv': ['araba', 'otomotiv', 'araç', 'üretim', 'satış']
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Metin sentiment analizi yapar
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            Sentiment skorları ve detayları
        """
        if not text:
            return {
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'positive_words': [],
                'negative_words': [],
                'sentiment': 'neutral'
            }
        
        # Metni küçük harfe çevir
        text_lower = text.lower()
        
        # Pozitif ve negatif kelimeleri say
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Toplam kelime sayısı
        total_words = len(text.split())
        
        if total_words == 0:
            return {
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'positive_words': [],
                'negative_words': [],
                'sentiment': 'neutral'
            }
        
        # Sentiment skoru hesapla (-1 ile 1 arası)
        sentiment_score = (positive_count - negative_count) / total_words
        
        # Güven skoru
        confidence = min(1.0, (positive_count + negative_count) / total_words)
        
        # Bulunan kelimeleri listele
        found_positive = [word for word in self.positive_words if word in text_lower]
        found_negative = [word for word in self.negative_words if word in text_lower]
        
        # Sentiment kategorisi
        if sentiment_score > 0.1:
            sentiment = 'positive'
        elif sentiment_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment_score': round(sentiment_score, 3),
            'confidence': round(confidence, 3),
            'positive_words': found_positive,
            'negative_words': found_negative,
            'sentiment': sentiment
        }
    
    def detect_sectors(self, text: str) -> List[str]:
        """
        Metinde geçen sektörleri tespit eder
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            Tespit edilen sektörler listesi
        """
        if not text:
            return []
        
        text_lower = text.lower()
        detected_sectors = []
        
        for sector, keywords in self.sector_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_sectors.append(sector)
        
        return detected_sectors
    
    def calculate_news_impact(self, sentiment_score: float, confidence: float, 
                            source_reliability: float = 0.5) -> Dict[str, float]:
        """
        Haber etkisini hesaplar
        
        Args:
            sentiment_score: Sentiment skoru
            confidence: Güven skoru
            source_reliability: Kaynak güvenilirliği (0-1 arası)
            
        Returns:
            Etki skorları
        """
        # Temel etki skoru
        base_impact = abs(sentiment_score) * confidence * source_reliability
        
        # Yön etkisi (pozitif/negatif)
        direction_impact = sentiment_score * confidence * source_reliability
        
        # Volatilite etkisi
        volatility_impact = base_impact * 0.3
        
        return {
            'base_impact': round(base_impact, 3),
            'direction_impact': round(direction_impact, 3),
            'volatility_impact': round(volatility_impact, 3),
            'overall_impact': round(base_impact + abs(direction_impact), 3)
        }
    
    def analyze_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """
        Haber listesini toplu analiz eder
        
        Args:
            news_list: Analiz edilecek haber listesi
            
        Returns:
            Analiz sonuçları
        """
        results = []
        
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            
            # Başlık ve içerik birleştir
            full_text = f"{title} {content}"
            
            # Sentiment analizi
            sentiment_result = self.analyze_sentiment(full_text)
            
            # Sektör tespiti
            sectors = self.detect_sectors(full_text)
            
            # Etki hesaplama
            impact = self.calculate_news_impact(
                sentiment_result['sentiment_score'],
                sentiment_result['confidence']
            )
            
            # Sonuçları birleştir
            analysis_result = {
                'news_id': news.get('id', ''),
                'title': title,
                'sentiment': sentiment_result,
                'sectors': sectors,
                'impact': impact,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            results.append(analysis_result)
        
        return results
    
    def get_market_sentiment_summary(self, news_list: List[Dict]) -> Dict:
        """
        Piyasa genel sentiment özeti
        
        Args:
            news_list: Haber listesi
            
        Returns:
            Piyasa sentiment özeti
        """
        if not news_list:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'positive_news_count': 0,
                'negative_news_count': 0,
                'neutral_news_count': 0,
                'top_sectors': [],
                'market_mood': 'balanced'
            }
        
        # Tüm haberleri analiz et
        analyses = self.analyze_news_batch(news_list)
        
        # Sentiment sayıları
        positive_count = sum(1 for a in analyses if a['sentiment']['sentiment'] == 'positive')
        negative_count = sum(1 for a in analyses if a['sentiment']['sentiment'] == 'negative')
        neutral_count = sum(1 for a in analyses if a['sentiment']['sentiment'] == 'neutral')
        
        # Ortalama sentiment skoru
        avg_sentiment = sum(a['sentiment']['sentiment_score'] for a in analyses) / len(analyses)
        
        # Ortalama güven skoru
        avg_confidence = sum(a['sentiment']['confidence'] for a in analyses) / len(analyses)
        
        # En çok geçen sektörler
        all_sectors = []
        for analysis in analyses:
            all_sectors.extend(analysis['sectors'])
        
        sector_counts = {}
        for sector in all_sectors:
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        top_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_sectors = [sector for sector, count in top_sectors]
        
        # Genel sentiment
        if avg_sentiment > 0.1:
            overall_sentiment = 'positive'
        elif avg_sentiment < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Piyasa ruh hali
        if overall_sentiment == 'positive':
            market_mood = 'bullish'
        elif overall_sentiment == 'negative':
            market_mood = 'bearish'
        else:
            market_mood = 'balanced'
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(avg_sentiment, 3),
            'confidence': round(avg_confidence, 3),
            'positive_news_count': positive_count,
            'negative_news_count': negative_count,
            'neutral_news_count': neutral_count,
            'top_sectors': top_sectors,
            'market_mood': market_mood,
            'total_news_analyzed': len(analyses)
        }
    
    def generate_mock_analysis(self, news_count: int = 10) -> List[Dict]:
        """
        Mock haber analizi verisi oluşturur
        
        Args:
            news_count: Oluşturulacak haber sayısı
            
        Returns:
            Mock analiz verileri
        """
        mock_analyses = []
        
        for i in range(news_count):
            # Rastgele sentiment
            sentiment_options = ['positive', 'negative', 'neutral']
            sentiment = random.choice(sentiment_options)
            
            if sentiment == 'positive':
                sentiment_score = random.uniform(0.1, 0.8)
            elif sentiment == 'negative':
                sentiment_score = random.uniform(-0.8, -0.1)
            else:
                sentiment_score = random.uniform(-0.1, 0.1)
            
            confidence = random.uniform(0.3, 0.9)
            
            # Rastgele sektörler
            sectors = random.sample(list(self.sector_keywords.keys()), 
                                  random.randint(1, 2))
            
            # Etki hesaplama
            impact = self.calculate_news_impact(sentiment_score, confidence)
            
            analysis = {
                'news_id': f'news_{i+1}',
                'title': f'Mock Haber Başlığı {i+1}',
                'sentiment': {
                    'sentiment_score': round(sentiment_score, 3),
                    'confidence': round(confidence, 3),
                    'sentiment': sentiment,
                    'positive_words': random.sample(self.positive_words, 2) if sentiment == 'positive' else [],
                    'negative_words': random.sample(self.negative_words, 2) if sentiment == 'negative' else []
                },
                'sectors': sectors,
                'impact': impact,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            mock_analyses.append(analysis)
        
        return mock_analyses 