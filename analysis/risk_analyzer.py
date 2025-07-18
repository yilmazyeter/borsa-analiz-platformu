"""
Risk analizi modülü
Risk değerlendirmesi ve uyarı sistemi
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class RiskAnalyzer:
    def __init__(self):
        self.risk_thresholds = {
            'high_volatility': 5.0,  # %5'ten fazla günlük volatilite
            'low_volume': 0.5,       # Ortalama hacmin %50'sinden az
            'price_drop': -10,       # %10'dan fazla günlük düşüş
            'trend_reversal': -5,    # %5'ten fazla trend tersine dönüş
            'support_break': 0.95    # Destek seviyesinin %95'ini kırmak
        }
    
    def analyze_volatility_risk(self, stock_data, days=365):
        """
        Volatilite riskini analiz eder
        """
        try:
            if not stock_data or 'historical_data' not in stock_data:
                return None
            
            df = pd.DataFrame(stock_data['historical_data'])
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').tail(days)
            
            if len(df) < 10:
                return None
            
            # Günlük getiri hesaplama
            df['Daily_Return'] = df['Close'].pct_change()
            
            # Volatilite hesaplamaları
            volatility = df['Daily_Return'].std() * 100
            annualized_volatility = volatility * np.sqrt(252)  # Yıllık volatilite
            
            # VaR (Value at Risk) hesaplama
            var_95 = np.percentile(df['Daily_Return'].dropna(), 5) * 100
            var_99 = np.percentile(df['Daily_Return'].dropna(), 1) * 100
            
            # Maksimum drawdown
            df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod()
            df['Rolling_Max'] = df['Cumulative_Return'].expanding().max()
            df['Drawdown'] = (df['Cumulative_Return'] - df['Rolling_Max']) / df['Rolling_Max'] * 100
            max_drawdown = df['Drawdown'].min()
            
            # Risk seviyesi belirleme
            if annualized_volatility < 20:
                risk_level = "DÜŞÜK"
                risk_score = 20
            elif annualized_volatility < 40:
                risk_level = "ORTA"
                risk_score = 50
            else:
                risk_level = "YÜKSEK"
                risk_score = 80
            
            return {
                'volatility': volatility,
                'annualized_volatility': annualized_volatility,
                'var_95': var_95,
                'var_99': var_99,
                'max_drawdown': max_drawdown,
                'risk_level': risk_level,
                'risk_score': risk_score
            }
            
        except Exception as e:
            print(f"Volatilite risk analizi hatası: {str(e)}")
            return None

    def analyze_volume_risk(self, stock_data, days=365):
        """
        Hacim riskini analiz eder
        """
        try:
            if not stock_data or 'historical_data' not in stock_data:
                return None
            
            df = pd.DataFrame(stock_data['historical_data'])
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').tail(days)
            
            if len(df) < 10:
                return None
            
            # Hacim analizi
            avg_volume = df['Volume'].mean()
            current_volume = df['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Hacim volatilitesi
            volume_volatility = df['Volume'].std() / df['Volume'].mean() * 100
            
            # Düşük hacim günleri
            low_volume_days = len(df[df['Volume'] < avg_volume * 0.5])
            low_volume_ratio = low_volume_days / len(df) * 100
            
            # Risk seviyesi belirleme
            if volume_ratio > 1.5 and volume_volatility < 50:
                risk_level = "DÜŞÜK"
                risk_score = 20
            elif volume_ratio > 0.8 and volume_volatility < 100:
                risk_level = "ORTA"
                risk_score = 50
            else:
                risk_level = "YÜKSEK"
                risk_score = 80
            
            return {
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'volume_volatility': volume_volatility,
                'low_volume_ratio': low_volume_ratio,
                'risk_level': risk_level,
                'risk_score': risk_score
            }
            
        except Exception as e:
            print(f"Hacim risk analizi hatası: {str(e)}")
            return None

    def analyze_price_risk(self, stock_data, days=365):
        """
        Fiyat riskini analiz eder
        """
        try:
            if not stock_data or 'historical_data' not in stock_data:
                return None
            
            df = pd.DataFrame(stock_data['historical_data'])
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').tail(days)
            
            if len(df) < 10:
                return None
            
            # Fiyat analizi
            current_price = df['Close'].iloc[-1]
            start_price = df['Close'].iloc[0]
            total_change = ((current_price - start_price) / start_price) * 100
            
            # Destek ve direnç seviyeleri
            support_level = df['Low'].min()
            resistance_level = df['High'].max()
            
            # Fiyat pozisyonu
            price_position = ((current_price - support_level) / (resistance_level - support_level)) * 100
            
            # Aşırı alım/satım durumu
            if price_position > 80:
                overbought_oversold = "AŞIRI ALIM"
                risk_score = 70
            elif price_position < 20:
                overbought_oversold = "AŞIRI SATIM"
                risk_score = 30
            else:
                overbought_oversold = "NORMAL"
                risk_score = 50
            
            # Trend riski
            if total_change < -20:
                trend_risk = "YÜKSEK"
                risk_score += 20
            elif total_change > 50:
                trend_risk = "ORTA"
                risk_score += 10
            else:
                trend_risk = "DÜŞÜK"
            
            # Genel risk seviyesi
            if risk_score < 40:
                risk_level = "DÜŞÜK"
            elif risk_score < 70:
                risk_level = "ORTA"
            else:
                risk_level = "YÜKSEK"
            
            return {
                'current_price': current_price,
                'total_change': total_change,
                'support_level': support_level,
                'resistance_level': resistance_level,
                'price_position': price_position,
                'overbought_oversold': overbought_oversold,
                'trend_risk': trend_risk,
                'risk_level': risk_level,
                'risk_score': risk_score
            }
            
        except Exception as e:
            print(f"Fiyat risk analizi hatası: {str(e)}")
            return None
    
    def analyze_market_risk(self, stock_data, market_data=None):
        """
        Piyasa riskini analiz eder
        
        Args:
            stock_data (dict): Hisse verileri
            market_data (dict): Piyasa verileri (opsiyonel)
        
        Returns:
            dict: Piyasa risk analizi
        """
        # Beta hesaplama (basit versiyon)
        if 'historical_data' not in stock_data:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        
        if len(df) < 20:
            return None
        
        # Hisse getirisi
        df['Stock_Return'] = df['Close'].pct_change()
        
        # Basit beta hesaplama (gerçek uygulamada piyasa verisi gerekli)
        # Burada varsayımsal bir beta değeri kullanıyoruz
        beta = 1.2  # Varsayımsal beta
        
        # Risk seviyesi
        if beta > 1.5:
            risk_level = "YÜKSEK"
            risk_score = 70
        elif beta > 1.0:
            risk_level = "ORTA"
            risk_score = 40
        else:
            risk_level = "DÜŞÜK"
            risk_score = 20
        
        return {
            'symbol': stock_data['symbol'],
            'beta': beta,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'market_sensitivity': "Yüksek" if beta > 1.2 else "Normal"
        }
    
    def get_comprehensive_risk_analysis(self, stock_data, days=365):
        """
        Kapsamlı risk analizi yapar
        
        Args:
            stock_data (dict): Hisse verileri
            days (int): Analiz edilecek gün sayısı
        
        Returns:
            dict: Kapsamlı risk analizi
        """
        volatility_risk = self.analyze_volatility_risk(stock_data, days)
        volume_risk = self.analyze_volume_risk(stock_data, days)
        price_risk = self.analyze_price_risk(stock_data, days)
        market_risk = self.analyze_market_risk(stock_data)
        
        # Genel risk skoru hesapla
        risk_scores = []
        risk_factors = []
        
        if volatility_risk:
            risk_scores.append(volatility_risk['risk_score'])
            if volatility_risk['risk_level'] == "YÜKSEK":
                risk_factors.append(f"Yüksek volatilite: %{volatility_risk['volatility']:.2f}")
        
        if volume_risk:
            risk_scores.append(volume_risk['risk_score'])
            if volume_risk['risk_level'] == "YÜKSEK":
                risk_factors.append(volume_risk['risk_reason'])
        
        if price_risk:
            risk_scores.append(price_risk['risk_score'])
            risk_factors.extend(price_risk['risk_factors'])
        
        if market_risk:
            risk_scores.append(market_risk['risk_score'])
        
        # Ortalama risk skoru
        overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Genel risk seviyesi
        if overall_risk_score >= 60:
            overall_risk_level = "YÜKSEK"
            recommendation = "RİSK UYARISI - Dikkatli olun"
        elif overall_risk_score >= 35:
            overall_risk_level = "ORTA"
            recommendation = "Orta risk - Takip edin"
        else:
            overall_risk_level = "DÜŞÜK"
            recommendation = "Düşük risk - Normal seviye"
        
        return {
            'symbol': stock_data['symbol'],
            'overall_risk_level': overall_risk_level,
            'overall_risk_score': overall_risk_score,
            'recommendation': recommendation,
            'risk_factors': risk_factors,
            'volatility_risk': volatility_risk,
            'volume_risk': volume_risk,
            'price_risk': price_risk,
            'market_risk': market_risk,
            'analysis_date': datetime.now().isoformat()
        } 