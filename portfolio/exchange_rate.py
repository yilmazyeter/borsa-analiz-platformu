#!/usr/bin/env python3
"""
Güncel Döviz Kuru Servisi
"""

import requests
import json
import time
from typing import Dict, Optional
import logging

class ExchangeRateService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_timeout = 300  # 5 dakika
        self.last_update = 0
        
        # API endpoints
        self.apis = [
            "https://api.exchangerate-api.com/v4/latest/USD",
            "https://open.er-api.com/v6/latest/USD",
            "https://api.frankfurter.app/latest?from=USD&to=TRY"
        ]
    
    def get_usdt_to_try_rate(self) -> float:
        """USDT/TRY kurunu döndürür"""
        try:
            # Cache kontrolü
            if self._is_cache_valid():
                return self.cache.get('USDT_TRY', 30.0)
            
            # API'lerden kur çekme
            rate = self._fetch_exchange_rate()
            
            # Cache'e kaydet
            self.cache['USDT_TRY'] = rate
            self.last_update = time.time()
            
            self.logger.info(f"Güncel USDT/TRY kuru: {rate:.4f}")
            return rate
            
        except Exception as e:
            self.logger.error(f"Döviz kuru çekme hatası: {e}")
            # Hata durumunda varsayılan kur
            return 30.0
    
    def _is_cache_valid(self) -> bool:
        """Cache'in geçerli olup olmadığını kontrol eder"""
        return (time.time() - self.last_update) < self.cache_timeout
    
    def _fetch_exchange_rate(self) -> float:
        """API'lerden döviz kuru çeker"""
        for api_url in self.apis:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Farklı API formatları için
                    if 'rates' in data:
                        if 'TRY' in data['rates']:
                            return data['rates']['TRY']
                        elif 'EUR' in data['rates']:
                            # EUR/TRY kuru varsa USD/TRY hesapla
                            eur_try = data['rates']['TRY']
                            usd_eur = data['rates']['EUR']
                            return eur_try / usd_eur
                    
                    # Frankfurter API formatı
                    elif 'rates' in data and 'TRY' in data['rates']:
                        return data['rates']['TRY']
                
            except Exception as e:
                self.logger.warning(f"API hatası {api_url}: {e}")
                continue
        
        # Tüm API'ler başarısız olursa varsayılan değer
        self.logger.warning("Tüm API'ler başarısız, varsayılan kur kullanılıyor")
        return 30.0
    
    def get_multiple_rates(self) -> Dict[str, float]:
        """Birden fazla döviz kurunu döndürür"""
        try:
            if self._is_cache_valid():
                return self.cache
            
            # Ana kurları çek
            usdt_try = self.get_usdt_to_try_rate()
            
            rates = {
                'USDT_TRY': usdt_try,
                'USD_TRY': usdt_try,  # USDT ≈ USD
                'EUR_TRY': usdt_try * 0.85,  # Yaklaşık EUR/USD
                'BTC_TRY': usdt_try * 45000,  # Yaklaşık BTC/USD
                'ETH_TRY': usdt_try * 2500,   # Yaklaşık ETH/USD
            }
            
            self.cache.update(rates)
            return rates
            
        except Exception as e:
            self.logger.error(f"Çoklu kur çekme hatası: {e}")
            return {
                'USDT_TRY': 30.0,
                'USD_TRY': 30.0,
                'EUR_TRY': 25.5,
                'BTC_TRY': 1350000.0,
                'ETH_TRY': 75000.0,
            }
    
    def convert_usdt_to_try(self, usdt_amount: float) -> float:
        """USDT miktarını TL'ye çevirir"""
        rate = self.get_usdt_to_try_rate()
        return usdt_amount * rate
    
    def convert_try_to_usdt(self, try_amount: float) -> float:
        """TL miktarını USDT'ye çevirir"""
        rate = self.get_usdt_to_try_rate()
        return try_amount / rate

# Global instance
exchange_rate_service = ExchangeRateService() 