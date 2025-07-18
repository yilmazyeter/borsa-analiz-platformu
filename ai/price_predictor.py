"""
AI Fiyat Tahmini Modülü
Kısa ve orta vadeli hisse fiyat tahminleri
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PricePredictor:
    """AI tabanlı fiyat tahmini sınıfı"""
    
    def __init__(self):
        self.model_loaded = False
        self.prediction_history = {}
        
    def predict_price(self, symbol, historical_data, days=7):
        """
        Hisse fiyat tahmini yapar
        
        Args:
            symbol (str): Hisse sembolü
            historical_data (list): Geçmiş fiyat verileri
            days (int): Tahmin günü sayısı
            
        Returns:
            dict: Tahmin sonuçları
        """
        try:
            if not historical_data or len(historical_data) < 30:
                return None
                
            # Veriyi DataFrame'e çevir
            df = pd.DataFrame(historical_data)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Son 30 günlük veriyi al
            recent_data = df.tail(30)
            
            # Basit trend analizi
            current_price = recent_data['Close'].iloc[-1]
            price_30d_ago = recent_data['Close'].iloc[0]
            trend = (current_price - price_30d_ago) / price_30d_ago
            
            # Volatilite hesapla
            returns = recent_data['Close'].pct_change().dropna()
            volatility = returns.std()
            
            # AI tahmin algoritması (basit lineer regresyon + momentum)
            predictions = []
            confidence_scores = []
            
            for day in range(1, days + 1):
                # Trend bazlı tahmin
                trend_prediction = current_price * (1 + trend * day / 30)
                
                # Momentum faktörü
                momentum = recent_data['Close'].diff().mean()
                momentum_prediction = current_price + (momentum * day)
                
                # Ağırlıklı ortalama
                prediction = (trend_prediction * 0.6) + (momentum_prediction * 0.4)
                
                # Güven skoru (volatiliteye göre)
                confidence = max(0.3, 1 - (volatility * day))
                
                predictions.append(round(prediction, 2))
                confidence_scores.append(round(confidence, 2))
            
            # Trend yönü belirleme
            if trend > 0.05:
                trend_direction = "Yükseliş"
            elif trend < -0.05:
                trend_direction = "Düşüş"
            else:
                trend_direction = "Yatay"
            
            # Öneri oluşturma
            avg_confidence = np.mean(confidence_scores)
            if avg_confidence > 0.7 and trend > 0.03:
                recommendation = "Al"
            elif avg_confidence > 0.7 and trend < -0.03:
                recommendation = "Sat"
            else:
                recommendation = "Bekle"
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'predictions': predictions,
                'confidence_scores': confidence_scores,
                'trend': trend_direction,
                'recommendation': recommendation,
                'confidence': round(avg_confidence * 100, 1),
                'prediction_date': datetime.now().isoformat()
            }
            
            # Tahmin geçmişini kaydet
            self.prediction_history[symbol] = result
            
            return result
            
        except Exception as e:
            print(f"Fiyat tahmini hatası ({symbol}): {str(e)}")
            return None
    
    def get_prediction_accuracy(self, symbol):
        """Geçmiş tahminlerin doğruluğunu hesaplar"""
        if symbol not in self.prediction_history:
            return None
            
        # Basit doğruluk hesaplama (gerçek verilerle karşılaştırma)
        return {
            'symbol': symbol,
            'accuracy': 75.5,  # Mock değer
            'total_predictions': 10,
            'correct_predictions': 7
        }
    
    def get_market_sentiment(self, symbol):
        """Piyasa sentiment'ini analiz eder"""
        # Mock sentiment analizi
        sentiment_scores = {
            'technical': np.random.uniform(0.4, 0.8),
            'fundamental': np.random.uniform(0.3, 0.7),
            'news': np.random.uniform(0.2, 0.9),
            'social': np.random.uniform(0.1, 0.6)
        }
        
        overall_sentiment = np.mean(list(sentiment_scores.values()))
        
        return {
            'symbol': symbol,
            'overall_sentiment': round(overall_sentiment, 3),
            'sentiment_scores': sentiment_scores,
            'sentiment_label': 'Pozitif' if overall_sentiment > 0.5 else 'Negatif'
        } 