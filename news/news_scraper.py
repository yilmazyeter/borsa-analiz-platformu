"""
Dinamik Piyasa Haber Akışı Modülü
ABD ve BIST hisseleri için haber çekme ve analiz
"""

import requests
import json
from datetime import datetime, timedelta
import random

class NewsScraper:
    """Haber çekme ve analiz sınıfı"""
    
    def __init__(self):
        self.news_cache = {}
        self.cache_duration = 300  # 5 dakika cache
        self.last_update = {}
        
        # Mock haber kaynakları
        self.news_sources = {
            'us': [
                'Reuters', 'Bloomberg', 'CNBC', 'MarketWatch', 'Yahoo Finance',
                'Financial Times', 'Wall Street Journal', 'Investing.com'
            ],
            'tr': [
                'Bloomberg HT', 'Dünya', 'Para', 'Ekonomi', 'Borsa Gündem',
                'Finans Gündem', 'Yatırım Haberleri', 'Piyasa Analiz'
            ]
        }
        
        # Mock haber kategorileri
        self.news_categories = [
            'Teknoloji', 'Finans', 'Enerji', 'Sağlık', 'Otomotiv',
            'Perakende', 'Bankacılık', 'Emtia', 'Kripto', 'Ekonomi'
        ]
    
    def get_market_news(self, market='us', limit=10):
        """
        Piyasa haberlerini çeker
        
        Args:
            market (str): Piyasa ('us' veya 'tr')
            limit (int): Haber sayısı
            
        Returns:
            list: Haber listesi
        """
        try:
            # Cache kontrolü
            cache_key = f"{market}_{limit}"
            if self._is_cache_valid(cache_key):
                return self.news_cache.get(cache_key, [])
            
            # Mock haber verisi oluştur
            news_list = self._generate_mock_news(market, limit)
            
            # Cache'e kaydet
            self.news_cache[cache_key] = news_list
            self.last_update[cache_key] = datetime.now()
            
            return news_list
            
        except Exception as e:
            print(f"Haber çekme hatası: {str(e)}")
            return []
    
    def get_news_summary(self, market='us'):
        """
        Haber özeti oluşturur
        
        Args:
            market (str): Piyasa
            
        Returns:
            dict: Haber özeti
        """
        try:
            news_list = self.get_market_news(market, 20)
            
            if not news_list:
                return self._default_summary()
            
            # Sentiment analizi
            positive_count = sum(1 for news in news_list if news.get('sentiment') == 'positive')
            negative_count = sum(1 for news in news_list if news.get('sentiment') == 'negative')
            neutral_count = len(news_list) - positive_count - negative_count
            
            # Trend konular
            trending_topics = self._extract_trending_topics(news_list)
            
            # Piyasa sentiment'i
            if positive_count > negative_count:
                market_sentiment = 'Pozitif'
            elif negative_count > positive_count:
                market_sentiment = 'Negatif'
            else:
                market_sentiment = 'Nötr'
            
            return {
                'total_news': len(news_list),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'positive_ratio': (positive_count / len(news_list)) * 100 if news_list else 0,
                'negative_ratio': (negative_count / len(news_list)) * 100 if news_list else 0,
                'neutral_ratio': (neutral_count / len(news_list)) * 100 if news_list else 0,
                'market_sentiment': market_sentiment,
                'trending_topics': trending_topics,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Haber özeti hatası: {str(e)}")
            return self._default_summary()
    
    def get_stock_news(self, symbol, limit=5):
        """
        Belirli bir hisse için haber çeker
        
        Args:
            symbol (str): Hisse sembolü
            limit (int): Haber sayısı
            
        Returns:
            list: Hisse haberleri
        """
        try:
            # Cache kontrolü
            cache_key = f"stock_{symbol}_{limit}"
            if self._is_cache_valid(cache_key):
                return self.news_cache.get(cache_key, [])
            
            # Mock hisse haberleri
            news_list = self._generate_stock_news(symbol, limit)
            
            # Cache'e kaydet
            self.news_cache[cache_key] = news_list
            self.last_update[cache_key] = datetime.now()
            
            return news_list
            
        except Exception as e:
            print(f"Hisse haber çekme hatası ({symbol}): {str(e)}")
            return []
    
    def _generate_mock_news(self, market, limit):
        """Mock haber verisi oluşturur"""
        news_list = []
        sources = self.news_sources.get(market, self.news_sources['us'])
        
        for i in range(limit):
            # Rastgele haber oluştur
            category = random.choice(self.news_categories)
            source = random.choice(sources)
            sentiment = random.choice(['positive', 'negative', 'neutral'])
            
            # Sentiment'e göre başlık ve içerik
            if sentiment == 'positive':
                title = self._generate_positive_title(category, market)
                content = self._generate_positive_content(category, market)
            elif sentiment == 'negative':
                title = self._generate_negative_title(category, market)
                content = self._generate_negative_content(category, market)
            else:
                title = self._generate_neutral_title(category, market)
                content = self._generate_neutral_content(category, market)
            
            # Tarih oluştur
            days_ago = random.randint(0, 7)
            published_date = datetime.now() - timedelta(days=days_ago)
            
            # İlgili hisseler
            symbols = self._get_related_symbols(category, market)
            
            news = {
                'id': f"news_{market}_{i}",
                'title': title,
                'content': content,
                'source': source,
                'category': category,
                'sentiment': sentiment,
                'published_date': published_date.strftime('%Y-%m-%d %H:%M'),
                'symbols': symbols,
                'url': f"https://example.com/news/{i}",
                'importance': random.choice(['high', 'medium', 'low'])
            }
            
            news_list.append(news)
        
        return news_list
    
    def _generate_stock_news(self, symbol, limit):
        """Belirli hisse için mock haber oluşturur"""
        news_list = []
        
        for i in range(limit):
            sentiment = random.choice(['positive', 'negative', 'neutral'])
            
            if sentiment == 'positive':
                title = f"{symbol} hissesi yükseliş trendinde"
                content = f"{symbol} hissesi son günlerde güçlü performans gösteriyor. Analistler pozitif görüş bildiriyor."
            elif sentiment == 'negative':
                title = f"{symbol} hissesinde düşüş endişesi"
                content = f"{symbol} hissesi için risk faktörleri artıyor. Yatırımcılar dikkatli olmalı."
            else:
                title = f"{symbol} hissesi yatay hareket ediyor"
                content = f"{symbol} hissesi belirli bir yön göstermiyor. Piyasa beklemede."
            
            news = {
                'id': f"stock_{symbol}_{i}",
                'title': title,
                'content': content,
                'source': random.choice(self.news_sources['us']),
                'category': 'Finans',
                'sentiment': sentiment,
                'published_date': (datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d %H:%M'),
                'symbols': [symbol],
                'url': f"https://example.com/stock/{symbol}/news/{i}",
                'importance': random.choice(['high', 'medium', 'low'])
            }
            
            news_list.append(news)
        
        return news_list
    
    def _generate_positive_title(self, category, market):
        """Pozitif haber başlığı"""
        titles = {
            'Teknoloji': [
                'Teknoloji hisseleri yükseliş trendinde',
                'Yapay zeka şirketleri rekor kırıyor',
                'Siber güvenlik sektörü büyüyor'
            ],
            'Finans': [
                'Bankacılık sektörü güçlü kazanç açıklıyor',
                'Fintech şirketleri yatırımcıları memnun ediyor',
                'Kredi kalitesi iyileşiyor'
            ],
            'Enerji': [
                'Yenilenebilir enerji hisseleri yükseliyor',
                'Petrol fiyatları stabil seyrediyor',
                'Enerji verimliliği artıyor'
            ]
        }
        
        category_titles = titles.get(category, ['Piyasa olumlu sinyaller veriyor'])
        return random.choice(category_titles)
    
    def _generate_negative_title(self, category, market):
        """Negatif haber başlığı"""
        titles = {
            'Teknoloji': [
                'Teknoloji hisselerinde düşüş endişesi',
                'Chip kıtlığı devam ediyor',
                'Siber saldırılar artıyor'
            ],
            'Finans': [
                'Bankacılık sektöründe risk faktörleri',
                'Kredi riskleri artıyor',
                'Finansal piyasalar volatil'
            ],
            'Enerji': [
                'Enerji fiyatları yükseliyor',
                'Petrol arzı endişesi',
                'Enerji krizi riski'
            ]
        }
        
        category_titles = titles.get(category, ['Piyasa belirsizlik yaşıyor'])
        return random.choice(category_titles)
    
    def _generate_neutral_title(self, category, market):
        """Nötr haber başlığı"""
        titles = {
            'Teknoloji': [
                'Teknoloji sektöründe gelişmeler',
                'Yeni teknoloji trendleri',
                'Dijital dönüşüm devam ediyor'
            ],
            'Finans': [
                'Finansal piyasalar analizi',
                'Bankacılık sektörü raporu',
                'Küresel ekonomi güncellemesi'
            ],
            'Enerji': [
                'Enerji piyasası güncellemesi',
                'Petrol fiyatları analizi',
                'Enerji politikaları değerlendirmesi'
            ]
        }
        
        category_titles = titles.get(category, ['Piyasa güncellemesi'])
        return random.choice(category_titles)
    
    def _generate_positive_content(self, category, market):
        """Pozitif haber içeriği"""
        return f"{category} sektöründe olumlu gelişmeler yaşanıyor. Analistler pozitif görüş bildiriyor ve yatırımcılar iyimser."
    
    def _generate_negative_content(self, category, market):
        """Negatif haber içeriği"""
        return f"{category} sektöründe risk faktörleri artıyor. Yatırımcılar dikkatli olmalı ve portföylerini gözden geçirmeli."
    
    def _generate_neutral_content(self, category, market):
        """Nötr haber içeriği"""
        return f"{category} sektöründe karışık sinyaller var. Piyasa beklemede ve daha net yön arayışında."
    
    def _get_related_symbols(self, category, market):
        """Kategoriye göre ilgili hisse sembolleri"""
        symbol_map = {
            'Teknoloji': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'],
            'Finans': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Enerji': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
            'Sağlık': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
            'Otomotiv': ['TSLA', 'F', 'GM', 'TM', 'HMC']
        }
        
        return symbol_map.get(category, ['AAPL', 'MSFT', 'GOOGL'])
    
    def _extract_trending_topics(self, news_list):
        """Trend konuları çıkarır"""
        topics = []
        categories = [news['category'] for news in news_list]
        
        # En çok geçen kategoriler
        from collections import Counter
        category_counts = Counter(categories)
        
        for category, count in category_counts.most_common(3):
            if count > 1:
                topics.append(category)
        
        return topics[:5]
    
    def _is_cache_valid(self, cache_key):
        """Cache geçerliliğini kontrol eder"""
        if cache_key not in self.last_update:
            return False
        
        elapsed = datetime.now() - self.last_update[cache_key]
        return elapsed.total_seconds() < self.cache_duration
    
    def _default_summary(self):
        """Varsayılan haber özeti"""
        return {
            'total_news': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_ratio': 0,
            'negative_ratio': 0,
            'neutral_ratio': 0,
            'market_sentiment': 'Nötr',
            'trending_topics': [],
            'last_updated': datetime.now().isoformat()
        } 