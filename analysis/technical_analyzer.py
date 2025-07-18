"""
Teknik analiz modülü
RSI, MACD, Bollinger Bantları ve diğer teknik göstergeler
"""

import pandas as pd
import numpy as np
from datetime import datetime


class TechnicalAnalyzer:
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices, period=14):
        """
        RSI (Relative Strength Index) hesaplar
        
        Args:
            prices (pd.Series): Fiyat serisi
            period (int): RSI periyodu
        
        Returns:
            float: RSI değeri
        """
        if len(prices) < period + 1:
            return None
            
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """
        MACD (Moving Average Convergence Divergence) hesaplar
        
        Args:
            prices (pd.Series): Fiyat serisi
            fast (int): Hızlı MA periyodu
            slow (int): Yavaş MA periyodu
            signal (int): Sinyal çizgisi periyodu
        
        Returns:
            dict: MACD değerleri
        """
        if len(prices) < slow + signal:
            return None
            
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """
        Bollinger Bantları hesaplar
        
        Args:
            prices (pd.Series): Fiyat serisi
            period (int): MA periyodu
            std_dev (int): Standart sapma çarpanı
        
        Returns:
            dict: Bollinger Bantları değerleri
        """
        if len(prices) < period:
            return None
            
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        current_price = prices.iloc[-1]
        
        return {
            'upper_band': upper_band.iloc[-1],
            'middle_band': ma.iloc[-1],
            'lower_band': lower_band.iloc[-1],
            'bandwidth': (upper_band.iloc[-1] - lower_band.iloc[-1]) / ma.iloc[-1],
            'position': (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
        }
    
    def calculate_stochastic(self, high, low, close, k_period=14, d_period=3):
        """
        Stochastic Oscillator hesaplar
        
        Args:
            high (pd.Series): Yüksek fiyatlar
            low (pd.Series): Düşük fiyatlar
            close (pd.Series): Kapanış fiyatları
            k_period (int): %K periyodu
            d_period (int): %D periyodu
        
        Returns:
            dict: Stochastic değerleri
        """
        if len(close) < k_period + d_period:
            return None
            
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k_percent': k_percent.iloc[-1],
            'd_percent': d_percent.iloc[-1]
        }
    
    def analyze_technical_indicators(self, stock_data):
        """
        Tüm teknik göstergeleri analiz eder
        
        Args:
            stock_data (dict): Hisse verileri
        
        Returns:
            dict: Teknik analiz sonuçları
        """
        if 'historical_data' not in stock_data:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        
        if len(df) < 30:
            return None
        
        # Teknik göstergeleri hesapla
        rsi = self.calculate_rsi(df['Close'])
        macd = self.calculate_macd(df['Close'])
        bollinger = self.calculate_bollinger_bands(df['Close'])
        stochastic = self.calculate_stochastic(df['High'], df['Low'], df['Close'])
        
        # Sinyal analizi
        signals = []
        
        # RSI sinyalleri
        if rsi:
            if rsi > 70:
                signals.append("RSI aşırı alım bölgesinde (>70)")
            elif rsi < 30:
                signals.append("RSI aşırı satım bölgesinde (<30)")
        
        # MACD sinyalleri
        if macd:
            if macd['macd'] > macd['signal']:
                signals.append("MACD pozitif sinyal (MACD > Signal)")
            else:
                signals.append("MACD negatif sinyal (MACD < Signal)")
        
        # Bollinger Bantları sinyalleri
        if bollinger:
            current_price = df['Close'].iloc[-1]
            if current_price > bollinger['upper_band']:
                signals.append("Fiyat üst Bollinger bandının üzerinde")
            elif current_price < bollinger['lower_band']:
                signals.append("Fiyat alt Bollinger bandının altında")
        
        # Stochastic sinyalleri
        if stochastic:
            if stochastic['k_percent'] > 80:
                signals.append("Stochastic aşırı alım bölgesinde")
            elif stochastic['k_percent'] < 20:
                signals.append("Stochastic aşırı satım bölgesinde")
        
        return {
            'symbol': stock_data['symbol'],
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bollinger,
            'stochastic': stochastic,
            'signals': signals,
            'analysis_date': datetime.now().isoformat()
        }
    
    def get_technical_recommendation(self, technical_analysis):
        """
        Teknik analiz sonuçlarına göre öneri üretir
        
        Args:
            technical_analysis (dict): Teknik analiz sonuçları
        
        Returns:
            dict: Teknik öneri
        """
        if not technical_analysis:
            return None
        
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        # RSI analizi
        if technical_analysis['rsi']:
            if technical_analysis['rsi'] < 30:
                buy_signals += 1
                reasons.append("RSI aşırı satım bölgesinde")
            elif technical_analysis['rsi'] > 70:
                sell_signals += 1
                reasons.append("RSI aşırı alım bölgesinde")
        
        # MACD analizi
        if technical_analysis['macd']:
            if technical_analysis['macd']['macd'] > technical_analysis['macd']['signal']:
                buy_signals += 1
                reasons.append("MACD pozitif sinyal")
            else:
                sell_signals += 1
                reasons.append("MACD negatif sinyal")
        
        # Bollinger Bantları analizi
        if technical_analysis['bollinger_bands']:
            position = technical_analysis['bollinger_bands']['position']
            if position < 0.2:
                buy_signals += 1
                reasons.append("Fiyat alt Bollinger bandına yakın")
            elif position > 0.8:
                sell_signals += 1
                reasons.append("Fiyat üst Bollinger bandına yakın")
        
        # Stochastic analizi
        if technical_analysis['stochastic']:
            k_percent = technical_analysis['stochastic']['k_percent']
            if k_percent < 20:
                buy_signals += 1
                reasons.append("Stochastic aşırı satım")
            elif k_percent > 80:
                sell_signals += 1
                reasons.append("Stochastic aşırı alım")
        
        # Genel öneri
        if buy_signals > sell_signals:
            recommendation = "TEKNİK ALIM"
            confidence = (buy_signals / (buy_signals + sell_signals)) * 100
        elif sell_signals > buy_signals:
            recommendation = "TEKNİK SATIŞ"
            confidence = (sell_signals / (buy_signals + sell_signals)) * 100
        else:
            recommendation = "TEKNİK BEKLE"
            confidence = 50
        
        return {
            'symbol': technical_analysis['symbol'],
            'recommendation': recommendation,
            'confidence': confidence,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'reasons': reasons
        } 