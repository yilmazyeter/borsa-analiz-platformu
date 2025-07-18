"""
Trend analizi modülü
Fiyat trendleri, momentum ve yön analizi
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TrendAnalyzer:
    def __init__(self):
        pass
    
    def analyze_price_trend(self, stock_data, days=365):
        """
        Fiyat trendini analiz eder
        """
        try:
            if not stock_data or 'historical_data' not in stock_data:
                return None
            
            df = pd.DataFrame(stock_data['historical_data'])
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Son N günlük veriyi al
            recent_data = df.tail(days)
            
            if len(recent_data) < 10:
                return None
            
            # Trend hesaplamaları
            prices = recent_data['Close'].values
            
            # Basit trend hesaplama
            start_price = prices[0]
            end_price = prices[-1]
            total_change = ((end_price - start_price) / start_price) * 100
            
            # Trend yönü
            if total_change > 5:
                trend_direction = "YÜKSELEN"
            elif total_change < -5:
                trend_direction = "DÜŞEN"
            else:
                trend_direction = "YATAY"
            
            # Momentum (son 10 günlük değişim)
            recent_change = ((prices[-1] - prices[-10]) / prices[-10]) * 100 if len(prices) >= 10 else 0
            
            # Volatilite (standart sapma)
            volatility = np.std(prices) / np.mean(prices) * 100
            
            # Trend gücü (basit hesaplama)
            trend_strength = abs(total_change) / 10  # 0-10 arası skor
            
            return {
                'trend_direction': trend_direction,
                'total_change': total_change,
                'momentum': recent_change,
                'volatility': volatility,
                'trend_strength': trend_strength
            }
            
        except Exception as e:
            print(f"Trend analizi hatası: {str(e)}")
            return None

    def analyze_volume_trend(self, stock_data, days=365):
        """
        Hacim trendini analiz eder
        
        Args:
            stock_data (dict): Hisse verileri
            days (int): Analiz edilecek gün sayısı
        
        Returns:
            dict: Hacim analiz sonuçları
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
        
        # Hacim trendi
        df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
        volume_trend = df['Volume'].tail(5).mean() / df['Volume'].head(5).mean()
        
        # Fiyat-hacim ilişkisi
        price_change = df['Close'].pct_change()
        volume_change = df['Volume'].pct_change()
        
        # Pozitif hacim (fiyat artarken hacim artıyor mu?)
        positive_volume_days = 0
        negative_volume_days = 0
        
        for i in range(1, len(df)):
            if price_change.iloc[i] > 0 and volume_change.iloc[i] > 0:
                positive_volume_days += 1
            elif price_change.iloc[i] < 0 and volume_change.iloc[i] > 0:
                negative_volume_days += 1
        
        volume_quality = positive_volume_days / (positive_volume_days + negative_volume_days) if (positive_volume_days + negative_volume_days) > 0 else 0
        
        return {
            'symbol': stock_data['symbol'],
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'volume_trend': volume_trend,
            'volume_quality': volume_quality,
            'positive_volume_days': positive_volume_days,
            'negative_volume_days': negative_volume_days
        }
    
    def get_trend_recommendation(self, trend_analysis, volume_analysis):
        """
        Trend analizine göre öneri üretir
        
        Args:
            trend_analysis (dict): Trend analiz sonuçları
            volume_analysis (dict): Hacim analiz sonuçları
        
        Returns:
            dict: Öneri ve güven skoru
        """
        if not trend_analysis or not volume_analysis:
            return None
        
        recommendation = ""
        confidence = 0
        reasons = []
        
        # Trend yönü analizi
        if trend_analysis['trend_direction'] == "YÜKSELEN":
            if trend_analysis['momentum'] > 1:
                recommendation = "GÜÇLÜ ALIM"
                confidence += 30
                reasons.append("Yükseliş trendi ve pozitif momentum")
            else:
                recommendation = "ZAYIF ALIM"
                confidence += 15
                reasons.append("Yükseliş trendi")
        elif trend_analysis['trend_direction'] == "DÜŞEN":
            if trend_analysis['momentum'] < -1:
                recommendation = "GÜÇLÜ SATIŞ"
                confidence += 30
                reasons.append("Düşüş trendi ve negatif momentum")
            else:
                recommendation = "ZAYIF SATIŞ"
                confidence += 15
                reasons.append("Düşüş trendi")
        else:
            recommendation = "BEKLE"
            confidence += 5
            reasons.append("Yatay trend")
        
        # Hacim analizi
        if volume_analysis['volume_ratio'] > 1.5:
            confidence += 20
            reasons.append("Yüksek hacim")
        elif volume_analysis['volume_ratio'] < 0.5:
            confidence -= 10
            reasons.append("Düşük hacim")
        
        if volume_analysis['volume_quality'] > 0.6:
            confidence += 15
            reasons.append("Kaliteli hacim")
        
        # Volatilite analizi
        if trend_analysis['volatility'] > 5:
            confidence -= 10
            reasons.append("Yüksek volatilite")
        elif trend_analysis['volatility'] < 2:
            confidence += 10
            reasons.append("Düşük volatilite")
        
        # Güven skorunu sınırla
        confidence = max(0, min(100, confidence))
        
        return {
            'symbol': trend_analysis['symbol'],
            'recommendation': recommendation,
            'confidence': confidence,
            'reasons': reasons,
            'trend_direction': trend_analysis['trend_direction'],
            'momentum': trend_analysis['momentum'],
            'volume_ratio': volume_analysis['volume_ratio']
        } 