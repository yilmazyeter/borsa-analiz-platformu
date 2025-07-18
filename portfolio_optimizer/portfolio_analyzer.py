"""
Portföy Analiz Modülü
Portföy sağlık skoru ve optimizasyon önerileri
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class PortfolioAnalyzer:
    """Portföy analiz sınıfı"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # %2 risksiz faiz oranı
        self.market_return = 0.08   # %8 piyasa getirisi
        
    def analyze_portfolio(self, portfolio_data, market_data):
        """
        Portföy analizi yapar
        
        Args:
            portfolio_data (list): Portföy verileri
            market_data (dict): Piyasa verileri
            
        Returns:
            dict: Portföy analiz sonuçları
        """
        try:
            if not portfolio_data:
                return self._default_analysis()
            
            # Portföy metrikleri hesapla
            total_value = self._calculate_total_value(portfolio_data)
            total_cost = self._calculate_total_cost(portfolio_data)
            total_return = self._calculate_total_return(portfolio_data)
            
            # Risk analizi
            risk_metrics = self._calculate_risk_metrics(portfolio_data, market_data)
            
            # Çeşitlendirme analizi
            diversification = self._analyze_diversification(portfolio_data)
            
            # Sağlık skoru hesapla
            health_score = self._calculate_health_score(portfolio_data, risk_metrics, diversification)
            
            # Optimizasyon önerileri
            recommendations = self._generate_recommendations(portfolio_data, risk_metrics, diversification)
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_return': total_return,
                'return_percentage': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
                'risk_metrics': risk_metrics,
                'diversification': diversification,
                'health_score': health_score,
                'recommendations': recommendations,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Portföy analiz hatası: {str(e)}")
            return self._default_analysis()
    
    def _calculate_total_value(self, portfolio_data):
        """Toplam portföy değeri"""
        try:
            total = 0
            for item in portfolio_data:
                current_price = item.get('current_price', 0)
                shares = item.get('shares', 0)
                total += current_price * shares
            return total
        except Exception as e:
            return 0
    
    def _calculate_total_cost(self, portfolio_data):
        """Toplam maliyet"""
        try:
            total = 0
            for item in portfolio_data:
                avg_price = item.get('avg_price', 0)
                shares = item.get('shares', 0)
                total += avg_price * shares
            return total
        except Exception as e:
            return 0
    
    def _calculate_total_return(self, portfolio_data):
        """Toplam getiri"""
        try:
            total_value = self._calculate_total_value(portfolio_data)
            total_cost = self._calculate_total_cost(portfolio_data)
            return total_value - total_cost
        except Exception as e:
            return 0
    
    def _calculate_risk_metrics(self, portfolio_data, market_data):
        """Risk metrikleri hesaplar"""
        try:
            # Portföy ağırlıkları
            total_value = self._calculate_total_value(portfolio_data)
            weights = []
            returns = []
            
            for item in portfolio_data:
                symbol = item.get('symbol', '')
                shares = item.get('shares', 0)
                current_price = item.get('current_price', 0)
                avg_price = item.get('avg_price', 0)
                
                if total_value > 0:
                    weight = (current_price * shares) / total_value
                    weights.append(weight)
                    
                    # Getiri hesapla
                    if avg_price > 0:
                        return_rate = (current_price - avg_price) / avg_price
                        returns.append(return_rate)
                    else:
                        returns.append(0)
            
            if not weights or not returns:
                return self._default_risk_metrics()
            
            # Volatilite hesapla
            portfolio_return = np.average(returns, weights=weights)
            portfolio_volatility = np.sqrt(np.average([(r - portfolio_return)**2 for r in returns], weights=weights))
            
            # Sharpe oranı
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Beta hesapla (basit yaklaşım)
            beta = self._calculate_beta(portfolio_data, market_data)
            
            # VaR (Value at Risk) - basit hesaplama
            var_95 = portfolio_return - (1.645 * portfolio_volatility)
            
            return {
                'portfolio_return': round(portfolio_return * 100, 2),
                'portfolio_volatility': round(portfolio_volatility * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'beta': round(beta, 3),
                'var_95': round(var_95 * 100, 2),
                'risk_level': self._classify_risk_level(portfolio_volatility)
            }
            
        except Exception as e:
            print(f"Risk metrik hesaplama hatası: {str(e)}")
            return self._default_risk_metrics()
    
    def _calculate_beta(self, portfolio_data, market_data):
        """Portföy beta hesaplar"""
        try:
            # Basit beta hesaplama
            total_value = self._calculate_total_value(portfolio_data)
            weighted_beta = 0
            
            for item in portfolio_data:
                symbol = item.get('symbol', '')
                shares = item.get('shares', 0)
                current_price = item.get('current_price', 0)
                
                # Hisse beta'sı (varsayılan değerler)
                stock_beta = self._get_stock_beta(symbol)
                weight = (current_price * shares) / total_value if total_value > 0 else 0
                weighted_beta += stock_beta * weight
            
            return weighted_beta
            
        except Exception as e:
            return 1.0  # Varsayılan beta
    
    def _get_stock_beta(self, symbol):
        """Hisse beta değeri (basit yaklaşım)"""
        # Gerçek uygulamada bu değerler API'den alınır
        beta_values = {
            'AAPL': 1.2, 'MSFT': 1.1, 'GOOGL': 1.0, 'TSLA': 2.1, 'NVDA': 1.8,
            'AMZN': 1.3, 'META': 1.4, 'NFLX': 1.6, 'AMD': 1.9, 'INTC': 0.9
        }
        return beta_values.get(symbol, 1.0)
    
    def _classify_risk_level(self, volatility):
        """Risk seviyesi sınıflandırır"""
        if volatility < 0.15:
            return 'Düşük'
        elif volatility < 0.25:
            return 'Orta'
        else:
            return 'Yüksek'
    
    def _analyze_diversification(self, portfolio_data):
        """Çeşitlendirme analizi"""
        try:
            if not portfolio_data:
                return self._default_diversification()
            
            # Sektör dağılımı
            sectors = {}
            total_value = self._calculate_total_value(portfolio_data)
            
            for item in portfolio_data:
                symbol = item.get('symbol', '')
                shares = item.get('shares', 0)
                current_price = item.get('current_price', 0)
                
                sector = self._get_stock_sector(symbol)
                value = current_price * shares
                
                if sector in sectors:
                    sectors[sector] += value
                else:
                    sectors[sector] = value
            
            # Sektör ağırlıkları
            sector_weights = {}
            for sector, value in sectors.items():
                sector_weights[sector] = (value / total_value * 100) if total_value > 0 else 0
            
            # Çeşitlendirme skoru (Herfindahl-Hirschman Index)
            hhi = sum([weight**2 for weight in sector_weights.values()])
            
            # Çeşitlendirme seviyesi
            if hhi < 1500:
                diversification_level = 'İyi'
            elif hhi < 2500:
                diversification_level = 'Orta'
            else:
                diversification_level = 'Zayıf'
            
            return {
                'sector_weights': sector_weights,
                'hhi_index': round(hhi, 2),
                'diversification_level': diversification_level,
                'total_sectors': len(sectors),
                'largest_sector': max(sectors.keys(), key=lambda x: sectors[x]) if sectors else None,
                'largest_sector_weight': max(sector_weights.values()) if sector_weights else 0
            }
            
        except Exception as e:
            print(f"Çeşitlendirme analiz hatası: {str(e)}")
            return self._default_diversification()
    
    def _get_stock_sector(self, symbol):
        """Hisse sektörü"""
        # Gerçek uygulamada bu bilgi API'den alınır
        sector_map = {
            'AAPL': 'Teknoloji', 'MSFT': 'Teknoloji', 'GOOGL': 'Teknoloji',
            'TSLA': 'Otomotiv', 'NVDA': 'Teknoloji', 'AMZN': 'Perakende',
            'META': 'Teknoloji', 'NFLX': 'Medya', 'AMD': 'Teknoloji',
            'INTC': 'Teknoloji', 'JPM': 'Finans', 'BAC': 'Finans',
            'WFC': 'Finans', 'GS': 'Finans', 'MS': 'Finans'
        }
        return sector_map.get(symbol, 'Diğer')
    
    def _calculate_health_score(self, portfolio_data, risk_metrics, diversification):
        """Portföy sağlık skoru hesaplar"""
        try:
            score = 0
            
            # Getiri skoru (0-30 puan)
            return_pct = risk_metrics.get('portfolio_return', 0)
            if return_pct > 10:
                score += 30
            elif return_pct > 5:
                score += 20
            elif return_pct > 0:
                score += 10
            elif return_pct > -5:
                score += 5
            
            # Risk skoru (0-25 puan)
            volatility = risk_metrics.get('portfolio_volatility', 0)
            if volatility < 15:
                score += 25
            elif volatility < 25:
                score += 15
            elif volatility < 35:
                score += 5
            
            # Sharpe oranı skoru (0-20 puan)
            sharpe = risk_metrics.get('sharpe_ratio', 0)
            if sharpe > 1.0:
                score += 20
            elif sharpe > 0.5:
                score += 15
            elif sharpe > 0:
                score += 10
            
            # Çeşitlendirme skoru (0-25 puan)
            hhi = diversification.get('hhi_index', 0)
            if hhi < 1500:
                score += 25
            elif hhi < 2500:
                score += 15
            elif hhi < 3500:
                score += 5
            
            return min(max(score, 0), 100)
            
        except Exception as e:
            return 50
    
    def _generate_recommendations(self, portfolio_data, risk_metrics, diversification):
        """Optimizasyon önerileri oluşturur"""
        recommendations = []
        
        try:
            # Risk seviyesi önerileri
            risk_level = risk_metrics.get('risk_level', 'Orta')
            volatility = risk_metrics.get('portfolio_volatility', 0)
            
            if risk_level == 'Yüksek':
                recommendations.append({
                    'type': 'risk_reduction',
                    'priority': 'Yüksek',
                    'title': 'Risk Azaltma',
                    'description': 'Portföyünüz yüksek risk seviyesinde. Daha stabil hisseler ekleyerek riski azaltın.',
                    'action': 'Savunmacı hisseler (JNJ, PG, KO) ekleyin'
                })
            
            # Çeşitlendirme önerileri
            hhi = diversification.get('hhi_index', 0)
            largest_sector_weight = diversification.get('largest_sector_weight', 0)
            
            if hhi > 2500:
                recommendations.append({
                    'type': 'diversification',
                    'priority': 'Yüksek',
                    'title': 'Çeşitlendirme',
                    'description': 'Portföyünüz yeterince çeşitlendirilmemiş. Farklı sektörlerden hisse ekleyin.',
                    'action': 'Farklı sektörlerden hisse alın'
                })
            
            if largest_sector_weight > 50:
                recommendations.append({
                    'type': 'sector_concentration',
                    'priority': 'Orta',
                    'title': 'Sektör Yoğunluğu',
                    'description': f'Portföyünüzün %{largest_sector_weight:.1f}\'i tek sektörde. Risk dağıtın.',
                    'action': 'Diğer sektörlerden hisse ekleyin'
                })
            
            # Getiri optimizasyonu
            return_pct = risk_metrics.get('portfolio_return', 0)
            if return_pct < 0:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'Yüksek',
                    'title': 'Performans İyileştirme',
                    'description': 'Portföyünüz zarar ediyor. Performansı iyi hisseler ekleyin.',
                    'action': 'Güçlü temel göstergelere sahip hisseler araştırın'
                })
            
            # Beta optimizasyonu
            beta = risk_metrics.get('beta', 1.0)
            if beta > 1.5:
                recommendations.append({
                    'type': 'beta_reduction',
                    'priority': 'Orta',
                    'title': 'Beta Azaltma',
                    'description': 'Portföyünüz piyasadan daha volatil. Daha stabil hisseler ekleyin.',
                    'action': 'Düşük beta hisseler (utilities, consumer staples) ekleyin'
                })
            
            # Genel öneriler
            if not recommendations:
                recommendations.append({
                    'type': 'maintenance',
                    'priority': 'Düşük',
                    'title': 'Portföy Bakımı',
                    'description': 'Portföyünüz iyi durumda. Düzenli takip yapın.',
                    'action': 'Haftalık portföy değerlendirmesi yapın'
                })
            
            return recommendations
            
        except Exception as e:
            return [{
                'type': 'error',
                'priority': 'Düşük',
                'title': 'Analiz Hatası',
                'description': 'Portföy analizi sırasında hata oluştu.',
                'action': 'Tekrar deneyin'
            }]
    
    def _default_analysis(self):
        """Varsayılan analiz sonucu"""
        return {
            'total_value': 0,
            'total_cost': 0,
            'total_return': 0,
            'return_percentage': 0,
            'risk_metrics': self._default_risk_metrics(),
            'diversification': self._default_diversification(),
            'health_score': 0,
            'recommendations': [],
            'analysis_date': datetime.now().isoformat()
        }
    
    def _default_risk_metrics(self):
        """Varsayılan risk metrikleri"""
        return {
            'portfolio_return': 0,
            'portfolio_volatility': 0,
            'sharpe_ratio': 0,
            'beta': 1.0,
            'var_95': 0,
            'risk_level': 'Belirsiz'
        }
    
    def _default_diversification(self):
        """Varsayılan çeşitlendirme analizi"""
        return {
            'sector_weights': {},
            'hhi_index': 0,
            'diversification_level': 'Belirsiz',
            'total_sectors': 0,
            'largest_sector': None,
            'largest_sector_weight': 0
        } 