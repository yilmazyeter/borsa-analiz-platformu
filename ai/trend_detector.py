"""
Trend Kırılım Tespiti Modülü
Destek/direnç seviyeleri ve kırılım noktalarını tespit eder
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class TrendDetector:
    """Trend kırılım tespiti sınıfı"""
    
    def __init__(self):
        self.breakout_history = {}
        self.support_resistance_cache = {}
        
    def detect_breakouts(self, historical_data, symbol, lookback_days=30):
        """
        Trend kırılımlarını tespit eder
        
        Args:
            historical_data (list): Geçmiş fiyat verileri
            symbol (str): Hisse sembolü
            lookback_days (int): Geriye dönük analiz günü
            
        Returns:
            dict: Kırılım analizi sonuçları
        """
        try:
            if not historical_data or len(historical_data) < 30:
                return None
                
            # Veriyi DataFrame'e çevir
            df = pd.DataFrame(historical_data)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Son N günlük veriyi al
            recent_data = df.tail(lookback_days).copy()
            
            # Destek ve direnç seviyeleri
            support_resistance = self._find_support_resistance(recent_data)
            
            # Kırılım noktaları
            breakouts = self._detect_breakout_points(recent_data, support_resistance)
            
            # Trend analizi
            trend_analysis = self._analyze_trend(recent_data)
            
            result = {
                'symbol': symbol,
                'breakouts': breakouts,
                'support_resistance': support_resistance,
                'trend_analysis': trend_analysis,
                'analysis_date': datetime.now().isoformat(),
                'lookback_days': lookback_days
            }
            
            # Sonuçları cache'le
            self.breakout_history[symbol] = result
            
            return result
            
        except Exception as e:
            print(f"Trend kırılım tespiti hatası ({symbol}): {str(e)}")
            return None
    
    def _find_support_resistance(self, df):
        """Destek ve direnç seviyelerini bulur"""
        try:
            # Son 20 günlük veriyi kullan
            recent = df.tail(20)
            
            # Yerel maksimum ve minimum noktalar
            highs = recent['High'].nlargest(3)
            lows = recent['Low'].nsmallest(3)
            
            # Direnç seviyeleri (yüksek noktalar)
            resistance_levels = sorted(highs.values, reverse=True)
            
            # Destek seviyeleri (düşük noktalar)
            support_levels = sorted(lows.values)
            
            current_price = df['Close'].iloc[-1]
            
            # En yakın destek ve direnç
            nearest_resistance = None
            nearest_support = None
            
            for level in resistance_levels:
                if level > current_price:
                    nearest_resistance = level
                    break
            
            for level in support_levels:
                if level < current_price:
                    nearest_support = level
                    break
            
            # Fiyat pozisyonu
            if nearest_resistance and nearest_support:
                total_range = nearest_resistance - nearest_support
                price_position = ((current_price - nearest_support) / total_range) * 100
            else:
                price_position = 50
            
            return {
                'resistance_levels': resistance_levels,
                'support_levels': support_levels,
                'nearest_resistance': round(nearest_resistance, 2) if nearest_resistance else None,
                'nearest_support': round(nearest_support, 2) if nearest_support else None,
                'price_position': round(price_position, 1),
                'current_price': round(current_price, 2)
            }
            
        except Exception as e:
            print(f"Destek/direnç hesaplama hatası: {str(e)}")
            return {
                'resistance_levels': [],
                'support_levels': [],
                'nearest_resistance': None,
                'nearest_support': None,
                'price_position': 50,
                'current_price': 0
            }
    
    def _detect_breakout_points(self, df, support_resistance):
        """Kırılım noktalarını tespit eder"""
        try:
            breakouts = []
            current_price = df['Close'].iloc[-1]
            
            # Direnç kırılımı
            if support_resistance['nearest_resistance']:
                resistance = support_resistance['nearest_resistance']
                if current_price > resistance * 1.02:  # %2 üzerinde kırılım
                    breakouts.append({
                        'type': 'Direnç Kırılımı',
                        'date': df.index[-1].strftime('%Y-%m-%d'),
                        'price': round(current_price, 2),
                        'level': round(resistance, 2),
                        'strength': 'Güçlü',
                        'indicator': 'Fiyat Direnç Üzerinde'
                    })
            
            # Destek kırılımı
            if support_resistance['nearest_support']:
                support = support_resistance['nearest_support']
                if current_price < support * 0.98:  # %2 altında kırılım
                    breakouts.append({
                        'type': 'Destek Kırılımı',
                        'date': df.index[-1].strftime('%Y-%m-%d'),
                        'price': round(current_price, 2),
                        'level': round(support, 2),
                        'strength': 'Güçlü',
                        'indicator': 'Fiyat Destek Altında'
                    })
            
            # Trend kırılımları
            trend_breakouts = self._detect_trend_breakouts(df)
            breakouts.extend(trend_breakouts)
            
            return breakouts
            
        except Exception as e:
            print(f"Kırılım tespiti hatası: {str(e)}")
            return []
    
    def _detect_trend_breakouts(self, df):
        """Trend kırılımlarını tespit eder"""
        try:
            breakouts = []
            
            # SMA kırılımları
            df['SMA_5'] = df['Close'].rolling(window=5).mean()
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            
            current_price = df['Close'].iloc[-1]
            sma_5 = df['SMA_5'].iloc[-1]
            sma_20 = df['SMA_20'].iloc[-1]
            
            # Altın kesişim (Golden Cross)
            if sma_5 > sma_20 and df['SMA_5'].iloc[-2] <= df['SMA_20'].iloc[-2]:
                breakouts.append({
                    'type': 'Altın Kesişim',
                    'date': df.index[-1].strftime('%Y-%m-%d'),
                    'price': round(current_price, 2),
                    'strength': 'Orta',
                    'indicator': 'SMA5 > SMA20'
                })
            
            # Ölüm kesişimi (Death Cross)
            elif sma_5 < sma_20 and df['SMA_5'].iloc[-2] >= df['SMA_20'].iloc[-2]:
                breakouts.append({
                    'type': 'Ölüm Kesişimi',
                    'date': df.index[-1].strftime('%Y-%m-%d'),
                    'price': round(current_price, 2),
                    'strength': 'Orta',
                    'indicator': 'SMA5 < SMA20'
                })
            
            # Hacim kırılımı
            avg_volume = df['Volume'].rolling(window=10).mean().iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            
            if current_volume > avg_volume * 1.5:  # %50 fazla hacim
                breakouts.append({
                    'type': 'Hacim Kırılımı',
                    'date': df.index[-1].strftime('%Y-%m-%d'),
                    'price': round(current_price, 2),
                    'strength': 'Güçlü',
                    'indicator': f'Hacim {round(current_volume/avg_volume, 1)}x'
                })
            
            return breakouts
            
        except Exception as e:
            print(f"Trend kırılım tespiti hatası: {str(e)}")
            return []
    
    def _analyze_trend(self, df):
        """Trend analizi yapar"""
        try:
            # Fiyat trendi
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
            
            # Momentum
            momentum = df['Close'].diff().mean()
            
            # Volatilite
            volatility = df['Close'].pct_change().std() * 100
            
            # Trend gücü
            if abs(price_change) > 10:
                trend_strength = 'Güçlü'
            elif abs(price_change) > 5:
                trend_strength = 'Orta'
            else:
                trend_strength = 'Zayıf'
            
            # Trend yönü
            if price_change > 2:
                trend_direction = 'Yükseliş'
            elif price_change < -2:
                trend_direction = 'Düşüş'
            else:
                trend_direction = 'Yatay'
            
            return {
                'price_change_percent': round(price_change, 2),
                'momentum': round(momentum, 4),
                'volatility_percent': round(volatility, 2),
                'trend_strength': trend_strength,
                'trend_direction': trend_direction
            }
            
        except Exception as e:
            print(f"Trend analizi hatası: {str(e)}")
            return {
                'price_change_percent': 0,
                'momentum': 0,
                'volatility_percent': 0,
                'trend_strength': 'Belirsiz',
                'trend_direction': 'Belirsiz'
            }
    
    def get_breakout_summary(self, symbol):
        """Kırılım özeti döndürür"""
        if symbol not in self.breakout_history:
            return None
            
        history = self.breakout_history[symbol]
        breakouts = history.get('breakouts', [])
        
        return {
            'symbol': symbol,
            'total_breakouts': len(breakouts),
            'recent_breakouts': breakouts[-3:] if breakouts else [],
            'last_analysis': history.get('analysis_date'),
            'trend_direction': history.get('trend_analysis', {}).get('trend_direction', 'Belirsiz')
        } 