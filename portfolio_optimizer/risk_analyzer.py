"""
Portföy Risk Analiz Modülü - Risk Hesaplama ve Yönetimi
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import random
import json

class RiskAnalyzer:
    """Portföy risk analizi ve yönetimi sınıfı"""
    
    def __init__(self):
        self.risk_levels = {
            'low': {'max_volatility': 0.15, 'max_drawdown': 0.10, 'max_concentration': 0.20},
            'medium': {'max_volatility': 0.25, 'max_drawdown': 0.20, 'max_concentration': 0.30},
            'high': {'max_volatility': 0.40, 'max_drawdown': 0.35, 'max_concentration': 0.50}
        }
    
    def calculate_portfolio_volatility(self, portfolio_data: Dict) -> float:
        """
        Portföy volatilitesini hesaplar
        
        Args:
            portfolio_data: Portföy verileri
            
        Returns:
            Portföy volatilitesi
        """
        if not portfolio_data.get('positions'):
            return 0.0
        
        total_value = portfolio_data.get('total_value', 0)
        if total_value == 0:
            return 0.0
        
        # Ağırlıklı volatilite hesaplama
        weighted_volatility = 0.0
        
        for position in portfolio_data['positions']:
            weight = position.get('value', 0) / total_value
            volatility = position.get('volatility', 0.2)  # Varsayılan volatilite
            weighted_volatility += weight * volatility
        
        # Korelasyon etkisi (basitleştirilmiş)
        correlation_factor = 0.7  # Ortalama korelasyon
        portfolio_volatility = weighted_volatility * correlation_factor
        
        return round(portfolio_volatility, 4)
    
    def calculate_max_drawdown(self, portfolio_history: List[Dict]) -> float:
        """
        Maksimum drawdown hesaplar
        
        Args:
            portfolio_history: Portföy geçmişi
            
        Returns:
            Maksimum drawdown yüzdesi
        """
        if len(portfolio_history) < 2:
            return 0.0
        
        values = [entry.get('value', 0) for entry in portfolio_history]
        peak = values[0]
        max_drawdown = 0.0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return round(max_drawdown, 4)
    
    def calculate_concentration_risk(self, portfolio_data: Dict) -> Dict:
        """
        Konsantrasyon riskini hesaplar
        
        Args:
            portfolio_data: Portföy verileri
            
        Returns:
            Konsantrasyon risk analizi
        """
        if not portfolio_data.get('positions'):
            return {
                'concentration_score': 0.0,
                'highest_concentration': 0.0,
                'top_holdings': [],
                'risk_level': 'low'
            }
        
        total_value = portfolio_data.get('total_value', 0)
        if total_value == 0:
            return {
                'concentration_score': 0.0,
                'highest_concentration': 0.0,
                'top_holdings': [],
                'risk_level': 'low'
            }
        
        # Her pozisyonun ağırlığını hesapla
        weights = []
        for position in portfolio_data['positions']:
            weight = position.get('value', 0) / total_value
            weights.append(weight)
        
        # En yüksek konsantrasyon
        highest_concentration = max(weights) if weights else 0.0
        
        # Herfindahl-Hirschman Index (HHI) - konsantrasyon skoru
        hhi = sum(weight ** 2 for weight in weights)
        
        # Risk seviyesi belirleme
        if hhi < 0.15:
            risk_level = 'low'
        elif hhi < 0.25:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # En büyük pozisyonlar
        positions_with_weights = []
        for i, position in enumerate(portfolio_data['positions']):
            positions_with_weights.append({
                'symbol': position.get('symbol', ''),
                'weight': round(weights[i], 4),
                'value': position.get('value', 0)
            })
        
        # Ağırlığa göre sırala
        positions_with_weights.sort(key=lambda x: x['weight'], reverse=True)
        top_holdings = positions_with_weights[:5]
        
        return {
            'concentration_score': round(hhi, 4),
            'highest_concentration': round(highest_concentration, 4),
            'top_holdings': top_holdings,
            'risk_level': risk_level
        }
    
    def calculate_var(self, portfolio_data: Dict, confidence_level: float = 0.95) -> float:
        """
        Value at Risk (VaR) hesaplar
        
        Args:
            portfolio_data: Portföy verileri
            confidence_level: Güven seviyesi
            
        Returns:
            VaR değeri
        """
        if not portfolio_data.get('positions'):
            return 0.0
        
        total_value = portfolio_data.get('total_value', 0)
        if total_value == 0:
            return 0.0
        
        # Basitleştirilmiş VaR hesaplama
        portfolio_volatility = self.calculate_portfolio_volatility(portfolio_data)
        
        # Normal dağılım varsayımı ile VaR
        z_score = 1.645 if confidence_level == 0.95 else 2.326  # 95% ve 99% için
        var = total_value * portfolio_volatility * z_score
        
        return round(var, 2)
    
    def calculate_sharpe_ratio(self, portfolio_data: Dict, risk_free_rate: float = 0.02) -> float:
        """
        Sharpe oranını hesaplar
        
        Args:
            portfolio_data: Portföy verileri
            risk_free_rate: Risksiz faiz oranı
            
        Returns:
            Sharpe oranı
        """
        if not portfolio_data.get('positions'):
            return 0.0
        
        # Portföy getirisi (basitleştirilmiş)
        total_return = portfolio_data.get('total_return', 0.0)
        portfolio_volatility = self.calculate_portfolio_volatility(portfolio_data)
        
        if portfolio_volatility == 0:
            return 0.0
        
        sharpe_ratio = (total_return - risk_free_rate) / portfolio_volatility
        
        return round(sharpe_ratio, 4)
    
    def analyze_sector_risk(self, portfolio_data: Dict) -> Dict:
        """
        Sektör riskini analiz eder
        
        Args:
            portfolio_data: Portföy verileri
            
        Returns:
            Sektör risk analizi
        """
        if not portfolio_data.get('positions'):
            return {
                'sector_weights': {},
                'sector_risk': 'low',
                'diversification_score': 1.0
            }
        
        total_value = portfolio_data.get('total_value', 0)
        if total_value == 0:
            return {
                'sector_weights': {},
                'sector_risk': 'low',
                'diversification_score': 1.0
            }
        
        # Sektör ağırlıklarını hesapla
        sector_weights = {}
        for position in portfolio_data['positions']:
            sector = position.get('sector', 'unknown')
            value = position.get('value', 0)
            
            if sector not in sector_weights:
                sector_weights[sector] = 0
            
            sector_weights[sector] += value
        
        # Yüzdelik ağırlıklara çevir
        for sector in sector_weights:
            sector_weights[sector] = round(sector_weights[sector] / total_value, 4)
        
        # En yüksek sektör ağırlığı
        max_sector_weight = max(sector_weights.values()) if sector_weights else 0
        
        # Sektör riski belirleme
        if max_sector_weight < 0.3:
            sector_risk = 'low'
        elif max_sector_weight < 0.5:
            sector_risk = 'medium'
        else:
            sector_risk = 'high'
        
        # Çeşitlendirme skoru (sektör sayısına göre)
        diversification_score = min(1.0, len(sector_weights) / 10)
        
        return {
            'sector_weights': sector_weights,
            'sector_risk': sector_risk,
            'diversification_score': round(diversification_score, 3),
            'max_sector_weight': round(max_sector_weight, 4)
        }
    
    def calculate_beta(self, portfolio_data: Dict, market_data: Dict) -> float:
        """
        Portföy beta değerini hesaplar
        
        Args:
            portfolio_data: Portföy verileri
            market_data: Piyasa verileri
            
        Returns:
            Beta değeri
        """
        if not portfolio_data.get('positions') or not market_data:
            return 1.0
        
        total_value = portfolio_data.get('total_value', 0)
        if total_value == 0:
            return 1.0
        
        # Ağırlıklı beta hesaplama
        weighted_beta = 0.0
        
        for position in portfolio_data['positions']:
            weight = position.get('value', 0) / total_value
            beta = position.get('beta', 1.0)  # Varsayılan beta
            weighted_beta += weight * beta
        
        return round(weighted_beta, 3)
    
    def generate_risk_report(self, portfolio_data: Dict, portfolio_history: List[Dict] = None) -> Dict:
        """
        Kapsamlı risk raporu oluşturur
        
        Args:
            portfolio_data: Portföy verileri
            portfolio_history: Portföy geçmişi (opsiyonel)
            
        Returns:
            Risk raporu
        """
        # Temel risk metrikleri
        volatility = self.calculate_portfolio_volatility(portfolio_data)
        concentration = self.calculate_concentration_risk(portfolio_data)
        sector_risk = self.analyze_sector_risk(portfolio_data)
        
        # VaR hesaplama
        var_95 = self.calculate_var(portfolio_data, 0.95)
        var_99 = self.calculate_var(portfolio_data, 0.99)
        
        # Sharpe oranı
        sharpe_ratio = self.calculate_sharpe_ratio(portfolio_data)
        
        # Maksimum drawdown
        max_drawdown = 0.0
        if portfolio_history:
            max_drawdown = self.calculate_max_drawdown(portfolio_history)
        
        # Genel risk seviyesi
        risk_score = 0
        risk_factors = []
        
        if volatility > 0.3:
            risk_score += 2
            risk_factors.append('Yüksek volatilite')
        elif volatility > 0.2:
            risk_score += 1
            risk_factors.append('Orta volatilite')
        
        if concentration['concentration_score'] > 0.25:
            risk_score += 2
            risk_factors.append('Yüksek konsantrasyon')
        elif concentration['concentration_score'] > 0.15:
            risk_score += 1
            risk_factors.append('Orta konsantrasyon')
        
        if sector_risk['sector_risk'] == 'high':
            risk_score += 2
            risk_factors.append('Sektör yoğunlaşması')
        elif sector_risk['sector_risk'] == 'medium':
            risk_score += 1
            risk_factors.append('Orta sektör riski')
        
        if max_drawdown > 0.25:
            risk_score += 2
            risk_factors.append('Yüksek drawdown')
        elif max_drawdown > 0.15:
            risk_score += 1
            risk_factors.append('Orta drawdown')
        
        # Risk seviyesi belirleme
        if risk_score <= 2:
            overall_risk = 'low'
        elif risk_score <= 4:
            overall_risk = 'medium'
        else:
            overall_risk = 'high'
        
        # Risk önerileri
        recommendations = []
        
        if volatility > 0.25:
            recommendations.append('Volatiliteyi azaltmak için daha stabil hisseler ekleyin')
        
        if concentration['concentration_score'] > 0.2:
            recommendations.append('Portföyü daha fazla çeşitlendirin')
        
        if sector_risk['sector_risk'] == 'high':
            recommendations.append('Farklı sektörlerden hisseler ekleyin')
        
        if max_drawdown > 0.2:
            recommendations.append('Stop-loss stratejileri uygulayın')
        
        return {
            'overall_risk': overall_risk,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'metrics': {
                'volatility': volatility,
                'concentration': concentration,
                'sector_risk': sector_risk,
                'var_95': var_95,
                'var_99': var_99,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_mock_risk_data(self) -> Dict:
        """
        Mock risk analiz verisi oluşturur
        
        Returns:
            Mock risk verileri
        """
        # Mock portföy verileri
        mock_portfolio = {
            'total_value': 100000,
            'total_return': 0.08,
            'positions': [
                {
                    'symbol': 'AAPL',
                    'value': 25000,
                    'volatility': 0.25,
                    'beta': 1.2,
                    'sector': 'teknoloji'
                },
                {
                    'symbol': 'MSFT',
                    'value': 20000,
                    'volatility': 0.22,
                    'beta': 1.1,
                    'sector': 'teknoloji'
                },
                {
                    'symbol': 'JPM',
                    'value': 15000,
                    'volatility': 0.18,
                    'beta': 0.9,
                    'sector': 'finans'
                },
                {
                    'symbol': 'JNJ',
                    'value': 15000,
                    'volatility': 0.15,
                    'beta': 0.7,
                    'sector': 'sağlık'
                },
                {
                    'symbol': 'XOM',
                    'value': 10000,
                    'volatility': 0.30,
                    'beta': 1.3,
                    'sector': 'enerji'
                },
                {
                    'symbol': 'KO',
                    'value': 5000,
                    'volatility': 0.12,
                    'beta': 0.6,
                    'sector': 'tüketim'
                }
            ]
        }
        
        # Mock portföy geçmişi
        mock_history = []
        base_value = 100000
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            # Rastgele değişim
            change = random.uniform(-0.03, 0.03)
            base_value *= (1 + change)
            mock_history.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(base_value, 2)
            })
        
        # Risk raporu oluştur
        risk_report = self.generate_risk_report(mock_portfolio, mock_history)
        
        return {
            'portfolio': mock_portfolio,
            'history': mock_history,
            'risk_report': risk_report
        } 