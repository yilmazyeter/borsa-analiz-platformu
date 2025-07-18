"""
Hisse senedi veri çekme modülü
Twelve Data API kullanarak hisse verilerini çeker
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Twelve Data API Key (ücretsiz kayıt: https://twelvedata.com/register)
TWELVE_DATA_API_KEY = "0972e9caa03b454fad5eadca558d6eb8"

class StockScraper:
    def __init__(self):
        pass

    def get_stock_data(self, symbol, period="1y"):
        """Mock data kullanarak hisse verisi çeker (API kredi limiti nedeniyle)"""
        try:
            print(f"Mock data kullanılıyor: {symbol}")
            
            # Mock data oluştur
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Gerçekçi fiyat aralıkları
            base_price = np.random.uniform(50, 500)
            current_price = base_price * np.random.uniform(0.8, 1.2)
            
            # 365 günlük veri oluştur
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Trend oluştur
            if np.random.random() < 0.3:  # %30 ihtimalle büyük düşüş
                trend = np.random.uniform(-0.8, -0.4)  # %40-80 düşüş
            else:
                trend = np.random.uniform(-0.2, 0.3)  # %20 düşüş - %30 artış
                
            # Günlük volatilite
            volatility = np.random.uniform(0.02, 0.05)
            
            # Fiyat serisi oluştur
            prices = [base_price]
            for i in range(1, len(dates)):
                change = trend/365 + np.random.normal(0, volatility)
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1))
                
            # DataFrame oluştur
            df = pd.DataFrame({
                'close': prices,
                'high': [p * (1 + np.random.uniform(0, 0.05)) for p in prices],
                'low': [p * (1 - np.random.uniform(0, 0.05)) for p in prices],
                'open': [p * (1 + np.random.uniform(-0.02, 0.02)) for p in prices],
                'volume': [np.random.randint(1000000, 10000000) for _ in prices]
            }, index=dates)
            
            current_price = df['close'].iloc[-1]
            price_365d_ago = df['close'].iloc[0]
            change_365d = ((current_price - price_365d_ago) / price_365d_ago) * 100
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_365d_ago': price_365d_ago,
                'change_365d': change_365d,
                'data': df,
                'source': 'mock_data',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Mock data oluşturma hatası ({symbol}): {str(e)}")
            return None
            
    def get_mock_stock_data(self, symbol, period="1y"):
        """Mock veri oluşturur (API limiti aşıldığında)"""
        try:
            # Gerçekçi mock veri oluştur
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Rastgele başlangıç fiyatı (50-500 arası)
            base_price = np.random.uniform(50, 500)
            
            # 365 günlük veri oluştur
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Trend oluştur (bazı hisseler düşüş trendinde)
            if np.random.random() < 0.3:  # %30 ihtimalle büyük düşüş
                trend = np.random.uniform(-0.8, -0.4)  # %40-80 düşüş
            else:
                trend = np.random.uniform(-0.2, 0.3)  # %20 düşüş - %30 artış
                
            # Günlük volatilite
            volatility = np.random.uniform(0.02, 0.05)
            
            # Fiyat serisi oluştur
            prices = [base_price]
            for i in range(1, len(dates)):
                # Trend + rastgele hareket
                change = trend/365 + np.random.normal(0, volatility)
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1))  # Minimum $1
                
            # DataFrame oluştur
            df = pd.DataFrame({
                'close': prices,
                'high': [p * (1 + np.random.uniform(0, 0.05)) for p in prices],
                'low': [p * (1 - np.random.uniform(0, 0.05)) for p in prices],
                'open': [p * (1 + np.random.uniform(-0.02, 0.02)) for p in prices],
                'volume': [np.random.randint(1000000, 10000000) for _ in prices]
            }, index=dates)
            
            current_price = df['close'].iloc[-1]
            price_365d_ago = df['close'].iloc[0]
            change_365d = ((current_price - price_365d_ago) / price_365d_ago) * 100
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_365d_ago': price_365d_ago,
                'change_365d': change_365d,
                'data': df,
                'source': 'mock_data',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Mock veri oluşturma hatası ({symbol}): {str(e)}")
            return None 

    def get_stock_data_with_fallback(self, symbol, period="1y"):
        """Hisse verisi çeker - şimdilik sadece mock data kullanıyor"""
        # API kredi limiti nedeniyle sadece mock data kullanıyoruz
        print(f"API kredi limiti nedeniyle mock data kullanılıyor: {symbol}")
        data = self.get_stock_data(symbol, period)
        
        return data 