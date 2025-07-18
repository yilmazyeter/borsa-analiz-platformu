"""
Haber çekme ve sentiment analizi modülü
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import re


class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_company_news(self, company_name, days=7):
        """
        Şirket haberlerini çeker
        
        Args:
            company_name (str): Şirket adı
            days (int): Kaç günlük haber aranacak
        
        Returns:
            list: Haber listesi
        """
        news_list = []
        
        # Örnek haber kaynakları (gerçek uygulamada API kullanılabilir)
        news_sources = [
            f"https://www.bloomberght.com/arama?q={company_name}",
            f"https://www.dunya.com/arama?q={company_name}",
            f"https://www.parafesor.com/arama?q={company_name}"
        ]
        
        for source in news_sources:
            try:
                response = self.session.get(source, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Haber başlıklarını bul (örnek selector'lar)
                    headlines = soup.find_all(['h1', 'h2', 'h3'], class_=re.compile(r'title|headline'))
                    
                    for headline in headlines[:5]:  # İlk 5 haberi al
                        news_item = {
                            'title': headline.get_text().strip(),
                            'source': source,
                            'date': datetime.now().isoformat(),
                            'url': headline.find('a')['href'] if headline.find('a') else source
                        }
                        news_list.append(news_item)
                        
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Haber çekme hatası ({source}): {str(e)}")
                continue
                
        return news_list
    
    def analyze_sentiment(self, text):
        """
        Basit sentiment analizi (gerçek uygulamada OpenAI veya HuggingFace kullanılır)
        
        Args:
            text (str): Analiz edilecek metin
        
        Returns:
            dict: Sentiment sonuçları
        """
        # Pozitif kelimeler
        positive_words = [
            'artış', 'yükseliş', 'büyüme', 'kâr', 'kazanç', 'olumlu', 'güçlü',
            'başarı', 'rekor', 'yüksek', 'iyi', 'mükemmel', 'harika'
        ]
        
        # Negatif kelimeler
        negative_words = [
            'düşüş', 'kayıp', 'zarar', 'olumsuz', 'zayıf', 'düşük', 'kötü',
            'kriz', 'problem', 'risk', 'tehlike', 'kaygı', 'endişe'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            score = positive_ratio
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            score = negative_ratio
        else:
            sentiment = 'neutral'
            score = 0
            
        confidence = max(positive_ratio, negative_ratio)
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def get_stock_news_sentiment(self, symbol, days=7):
        """
        Hisse için haber sentiment analizi yapar
        
        Args:
            symbol (str): Hisse sembolü
            days (int): Analiz edilecek gün sayısı
        
        Returns:
            dict: Sentiment analiz sonuçları
        """
        # Hisse adını sembolden çıkar (basit örnek)
        company_name = symbol.replace('.IS', '').replace('.', ' ')
        
        # Haberleri çek
        news_list = self.get_company_news(company_name, days)
        
        if not news_list:
            return {
                'symbol': symbol,
                'total_news': 0,
                'positive_news': 0,
                'negative_news': 0,
                'neutral_news': 0,
                'overall_sentiment': 'neutral',
                'sentiment_score': 0
            }
        
        # Her haber için sentiment analizi
        sentiments = []
        for news in news_list:
            sentiment = self.analyze_sentiment(news['title'])
            news['sentiment'] = sentiment
            sentiments.append(sentiment)
        
        # Genel sentiment hesapla
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral_count = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
        
        total_news = len(sentiments)
        
        if positive_count > negative_count:
            overall_sentiment = 'positive'
            sentiment_score = positive_count / total_news
        elif negative_count > positive_count:
            overall_sentiment = 'negative'
            sentiment_score = negative_count / total_news
        else:
            overall_sentiment = 'neutral'
            sentiment_score = 0
        
        return {
            'symbol': symbol,
            'total_news': total_news,
            'positive_news': positive_count,
            'negative_news': negative_count,
            'neutral_news': neutral_count,
            'overall_sentiment': overall_sentiment,
            'sentiment_score': sentiment_score,
            'news_list': news_list
        } 