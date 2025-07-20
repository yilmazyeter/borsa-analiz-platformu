#!/usr/bin/env python3
"""
Kripto Para Analiz Modülü
USDT üzerindeki coinlerin anlık analizi ve fırsat tespiti
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Tuple
import json
import os

class CryptoAnalyzer:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.exchange_info_url = f"{self.base_url}/exchangeInfo"
        self.klines_url = f"{self.base_url}/klines"
        self.ticker_url = f"{self.base_url}/ticker/24hr"
        
        # Analiz parametreleri
        self.min_volume_usdt = 1000000  # Minimum 1M USDT hacim
        self.min_price_change = 2.0  # Minimum %2 değişim
        self.opportunity_threshold = 5.0  # %5 düşüş fırsat eşiği
        
        # Cache için
        self.cache = {}
        self.cache_duration = 60  # 60 saniye cache
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_all_usdt_pairs(self) -> List[str]:
        """Binance'deki tüm USDT çiftlerini getirir"""
        try:
            response = requests.get(self.exchange_info_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            usdt_pairs = []
            
            for symbol_info in data['symbols']:
                symbol = symbol_info['symbol']
                if symbol.endswith('USDT') and symbol_info['status'] == 'TRADING':
                    usdt_pairs.append(symbol)
            
            self.logger.info(f"Toplam {len(usdt_pairs)} USDT çifti bulundu")
            return usdt_pairs
            
        except Exception as e:
            self.logger.error(f"USDT çiftleri alınırken hata: {e}")
            return []
    
    def get_coin_data(self, symbol: str, interval: str = "1h", limit: int = 168) -> Optional[Dict]:
        """Belirli bir coinin verilerini çeker (son 7 gün - 168 saat)"""
        try:
            # Cache kontrolü
            cache_key = f"{symbol}_{interval}_{limit}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if (datetime.now() - cache_time).seconds < self.cache_duration:
                    return cache_data
            
            url = f"{self.klines_url}?symbol={symbol}&interval={interval}&limit={limit}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return None
            
            # Veriyi DataFrame'e çevir
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Veri tiplerini düzelt
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Son fiyat bilgileri
            current_price = float(df['close'].iloc[-1])
            price_24h_ago = float(df['close'].iloc[-24]) if len(df) >= 24 else float(df['close'].iloc[0])
            price_7d_ago = float(df['close'].iloc[0])
            
            # Değişim hesaplamaları
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            change_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100
            
            # Hacim bilgileri
            volume_24h = float(df['quote_asset_volume'].iloc[-24:].sum()) if len(df) >= 24 else float(df['quote_asset_volume'].sum())
            
            # Sonuç verisi
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'price_24h_ago': price_24h_ago,
                'price_7d_ago': price_7d_ago,
                'change_24h': change_24h,
                'change_7d': change_7d,
                'volume_24h': volume_24h,
                'data': df,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache'e kaydet
            self.cache[cache_key] = (datetime.now(), result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"{symbol} verisi alınırken hata: {e}")
            return None
    
    def get_ticker_info(self, symbol: str) -> Optional[Dict]:
        """Coin'in 24 saatlik ticker bilgilerini getirir"""
        try:
            url = f"{self.ticker_url}?symbol={symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': data['symbol'],
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'weighted_avg_price': float(data['weightedAvgPrice']),
                'prev_close_price': float(data['prevClosePrice']),
                'last_price': float(data['lastPrice']),
                'last_qty': float(data['lastQty']),
                'bid_price': float(data['bidPrice']),
                'ask_price': float(data['askPrice']),
                'open_price': float(data['openPrice']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'open_time': datetime.fromtimestamp(data['openTime'] / 1000),
                'close_time': datetime.fromtimestamp(data['closeTime'] / 1000),
                'count': int(data['count'])
            }
            
        except Exception as e:
            self.logger.error(f"{symbol} ticker bilgisi alınırken hata: {e}")
            return None
    
    def analyze_coin_opportunity(self, coin_data: Dict) -> Dict:
        """Coin'in fırsat analizini yapar"""
        if not coin_data:
            return {}
        
        symbol = coin_data['symbol']
        current_price = coin_data['current_price']
        change_24h = coin_data['change_24h']
        change_7d = coin_data['change_7d']
        volume_24h = coin_data['volume_24h']
        
        # Fırsat skoru hesaplama
        opportunity_score = 0
        opportunity_type = "Nötr"
        recommendation = "Bekle"
        
        # 1. Hacim kontrolü
        if volume_24h < self.min_volume_usdt:
            return {
                'symbol': symbol,
                'opportunity_score': 0,
                'opportunity_type': "Düşük Hacim",
                'recommendation': "Hacim yetersiz",
                'reason': f"24h hacim: ${volume_24h:,.0f} (min: ${self.min_volume_usdt:,.0f})"
            }
        
        # 2. Düşüş analizi (fırsat tespiti)
        if change_7d < -self.opportunity_threshold:
            opportunity_score += abs(change_7d) * 2  # Düşüş ne kadar büyükse o kadar iyi fırsat
            opportunity_type = "Düşüş Fırsatı"
            recommendation = "Alım Fırsatı"
        
        # 3. Son 24 saatte toparlanma
        if change_24h > 0 and change_7d < 0:
            opportunity_score += change_24h * 1.5  # Toparlanma başladı
            opportunity_type = "Toparlanma Fırsatı"
            recommendation = "Alım Fırsatı"
        
        # 4. Aşırı düşüş kontrolü
        if change_7d < -20:
            opportunity_score += 20  # Aşırı düşüş bonusu
            opportunity_type = "Aşırı Düşüş Fırsatı"
            recommendation = "Güçlü Alım"
        
        # 5. Hacim artışı kontrolü
        df = coin_data['data']
        if len(df) >= 48:
            volume_recent = df['quote_asset_volume'].iloc[-24:].sum()
            volume_previous = df['quote_asset_volume'].iloc[-48:-24].sum()
            if volume_previous > 0:
                volume_increase = ((volume_recent - volume_previous) / volume_previous) * 100
                if volume_increase > 50:  # %50 hacim artışı
                    opportunity_score += 10
                    opportunity_type += " + Hacim Artışı"
        
        # 6. Teknik göstergeler
        rsi = self.calculate_rsi(df['close'])
        if rsi < 30:
            opportunity_score += 15  # Aşırı satım
            opportunity_type += " + Aşırı Satım"
        
        # Sonuç
        return {
            'symbol': symbol,
            'current_price': current_price,
            'change_24h': change_24h,
            'change_7d': change_7d,
            'volume_24h': volume_24h,
            'opportunity_score': opportunity_score,
            'opportunity_type': opportunity_type,
            'recommendation': recommendation,
            'rsi': rsi if 'rsi' in locals() else None,
            'last_updated': datetime.now().isoformat()
        }
    
    def analyze_24h_profit_potential(self, coin_data: Dict) -> Dict:
        """24 saatlik kazanç potansiyelini analiz eder - uzun düşüşten sonra artış potansiyeli"""
        if not coin_data:
            return {}
        
        symbol = coin_data['symbol']
        current_price = coin_data['current_price']
        change_24h = coin_data['change_24h']
        change_7d = coin_data['change_7d']
        volume_24h = coin_data['volume_24h']
        
        # Teknik göstergeler
        df = coin_data['data']
        rsi = self.calculate_rsi(df['close'])
        
        # 24 saatlik kazanç potansiyeli skoru
        profit_score = 0
        recommendation = "Bekle"
        confidence = "Düşük"
        reasoning = []
        
        # 1. Uzun vadeli düşüş kontrolü (7 günlük düşüş)
        if change_7d < -10:  # Son 7 günde %10'dan fazla düşüş
            profit_score += 25
            reasoning.append(f"7 günde %{abs(change_7d):.1f} düşüş - toparlanma potansiyeli")
        elif change_7d < -5:
            profit_score += 15
            reasoning.append(f"7 günde %{abs(change_7d):.1f} düşüş")
        
        # 2. Son 24 saatte toparlanma başlangıcı
        if change_24h > 0 and change_7d < 0:
            profit_score += 30
            reasoning.append(f"24 saatte %{change_24h:.1f} artış başladı")
        elif change_24h > 2:  # Güçlü artış
            profit_score += 20
            reasoning.append(f"Güçlü 24 saat artış: %{change_24h:.1f}")
        
        # 3. RSI aşırı satım durumu (düşüşten sonra toparlanma sinyali)
        if rsi < 25:
            profit_score += 25
            reasoning.append(f"RSI aşırı satım: {rsi:.1f} - güçlü toparlanma sinyali")
        elif rsi < 35:
            profit_score += 15
            reasoning.append(f"RSI düşük: {rsi:.1f} - toparlanma potansiyeli")
        
        # 4. Hacim artışı analizi (düşüşten sonra hacim artışı)
        if len(df) >= 48:
            volume_recent = df['quote_asset_volume'].iloc[-24:].sum()
            volume_previous = df['quote_asset_volume'].iloc[-48:-24].sum()
            if volume_previous > 0:
                volume_increase = ((volume_recent - volume_previous) / volume_previous) * 100
                if volume_increase > 100:  # Hacim 2 katına çıktı
                    profit_score += 20
                    reasoning.append(f"Hacim %{volume_increase:.1f} arttı - güçlü alım sinyali")
                elif volume_increase > 50:
                    profit_score += 10
                    reasoning.append(f"Hacim %{volume_increase:.1f} arttı")
        
        # 5. Fiyat momentum analizi (son 6 saatte pozitif momentum)
        if len(df) >= 6:
            recent_prices = df['close'].iloc[-6:].values
            price_momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            if price_momentum > 3:
                profit_score += 15
                reasoning.append(f"Son 6 saatte %{price_momentum:.1f} momentum")
        
        # 6. Destek seviyesi testi (düşüşten sonra destek bulma)
        if len(df) >= 24:
            support_level = df['low'].iloc[-24:].min()
            if current_price <= support_level * 1.03:  # Destek seviyesine yakın
                profit_score += 10
                reasoning.append("Destek seviyesinde - düşüş durdu")
        
        # 7. Trend dönüşü sinyalleri (kısa vadeli trend pozitife dönüyor)
        if len(df) >= 12:
            sma_short = df['close'].iloc[-12:].mean()
            sma_long = df['close'].iloc[-24:].mean()
            if current_price > sma_short and sma_short > sma_long:
                profit_score += 15
                reasoning.append("Kısa vadeli trend pozitife döndü")
        
        # 8. Volatilite analizi (yüksek volatilite = fırsat)
        if len(df) >= 24:
            volatility = df['close'].iloc[-24:].pct_change().std() * 100
            if volatility > 8:  # Yüksek volatilite
                profit_score += 5
                reasoning.append("Yüksek volatilite - hızlı hareket potansiyeli")
        
        # 9. MACD sinyali (düşüşten sonra pozitif sinyal)
        if len(df) >= 26:
            macd_line, signal_line = self.calculate_macd(df['close'])
            if len(macd_line) > 0 and len(signal_line) > 0:
                if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                    profit_score += 10
                    reasoning.append("MACD pozitif sinyal - trend dönüşü")
        
        # 10. Bollinger Bands analizi (alt banda yakınlık)
        if len(df) >= 20:
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df['close'])
            if len(bb_lower) > 0:
                bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
                if bb_position < 0.2:  # Alt banda yakın
                    profit_score += 10
                    reasoning.append("Bollinger alt bandında - yükseliş potansiyeli")
        
        # Tavsiye belirleme
        if profit_score >= 70:
            recommendation = "KESİNLİKLE AL"
            confidence = "Çok Yüksek"
        elif profit_score >= 50:
            recommendation = "GÜÇLÜ AL"
            confidence = "Yüksek"
        elif profit_score >= 30:
            recommendation = "AL"
            confidence = "Orta"
        elif profit_score >= 15:
            recommendation = "İZLE"
            confidence = "Düşük"
        else:
            recommendation = "BEKLE"
            confidence = "Yok"
        
        # 24 saatlik hedef fiyat tahmini
        target_price = current_price
        if profit_score >= 30:
            # Düşüşten sonra toparlanma için %5-25 artış
            potential_gain = min(profit_score / 3, 25)  # Maksimum %25
            target_price = current_price * (1 + potential_gain / 100)
        
        return {
            'symbol': symbol,
            'profit_score': profit_score,
            'recommendation': recommendation,
            'confidence': confidence,
            'target_price': target_price,
            'potential_gain_percent': ((target_price - current_price) / current_price) * 100,
            'reasoning': reasoning,
            'rsi': rsi,
            'current_price': current_price,
            'change_24h': change_24h,
            'change_7d': change_7d,
            'volume_24h': volume_24h,
            'long_term_drop': change_7d < -5,  # Uzun vadeli düşüş flag'i
            'recovery_started': change_24h > 0 and change_7d < 0  # Toparlanma başladı flag'i
        }
    
    def find_24h_profit_opportunities(self, min_score: float = 20.0, max_results: int = 20) -> List[Dict]:
        """24 saatlik kazanç potansiyeli olan coinleri bulur"""
        try:
            # Tüm USDT çiftlerini al
            usdt_pairs = self.get_all_usdt_pairs()
            
            if not usdt_pairs:
                return []
            
            profit_opportunities = []
            
            # İlk 100 coin'i analiz et
            pairs_to_analyze = usdt_pairs[:100]
            
            self.logger.info(f"{len(pairs_to_analyze)} coin 24 saatlik kazanç potansiyeli için analiz ediliyor...")
            
            for i, symbol in enumerate(pairs_to_analyze):
                try:
                    # Rate limiting
                    if i % 10 == 0 and i > 0:
                        time.sleep(0.5)
                    
                    # Coin verisini al
                    coin_data = self.get_coin_data(symbol)
                    
                    if coin_data:
                        # 24 saatlik kazanç potansiyeli analizi
                        profit_analysis = self.analyze_24h_profit_potential(coin_data)
                        
                        if profit_analysis and profit_analysis.get('profit_score', 0) >= min_score:
                            profit_opportunities.append(profit_analysis)
                    
                except Exception as e:
                    self.logger.error(f"{symbol} 24 saatlik analiz edilirken hata: {e}")
                    continue
            
            # Skora göre sırala
            profit_opportunities.sort(key=lambda x: x.get('profit_score', 0), reverse=True)
            
            self.logger.info(f"{len(profit_opportunities)} 24 saatlik kazanç fırsatı bulundu")
            
            return profit_opportunities[:max_results]
            
        except Exception as e:
            self.logger.error(f"24 saatlik kazanç fırsatı arama hatası: {e}")
            return []
    
    def analyze_1h_profit_potential(self, coin_data: Dict) -> Dict:
        """1 saatlik kazanç potansiyeli analizi"""
        if not coin_data:
            return {}
        
        symbol = coin_data['symbol']
        current_price = coin_data['current_price']
        volume_24h = coin_data['volume_24h']
        df = coin_data['data']
        
        # 1 saatlik değişim hesaplama
        if len(df) >= 1:
            price_1h_ago = float(df['close'].iloc[-2]) if len(df) >= 2 else current_price
            change_1h = ((current_price - price_1h_ago) / price_1h_ago) * 100
        else:
            change_1h = 0
        
        # 4 saatlik değişim hesaplama
        if len(df) >= 4:
            price_4h_ago = float(df['close'].iloc[-5])
            change_4h = ((current_price - price_4h_ago) / price_4h_ago) * 100
        else:
            change_4h = 0
        
        # 1 saatlik fırsat skoru hesaplama
        opportunity_score = 0
        opportunity_type = "Nötr"
        recommendation = "Bekle"
        
        # 1. Hacim kontrolü
        if volume_24h < self.min_volume_usdt:
            return {
                'symbol': symbol,
                'opportunity_score': 0,
                'opportunity_type': "Düşük Hacim",
                'recommendation': "Hacim yetersiz",
                'reason': f"24h hacim: ${volume_24h:,.0f} (min: ${self.min_volume_usdt:,.0f})"
            }
        
        # 2. 1 saatlik düşüş analizi
        if change_1h < -5:  # %5'ten fazla düşüş
            opportunity_score += abs(change_1h) * 3  # Düşüş ne kadar büyükse o kadar iyi fırsat
            opportunity_type = "1h Düşüş Fırsatı"
            recommendation = "ACİL AL"
        
        elif change_1h < -3:  # %3-5 arası düşüş
            opportunity_score += abs(change_1h) * 2
            opportunity_type = "1h Düşüş Fırsatı"
            recommendation = "HIZLI AL"
        
        elif change_1h < -1:  # %1-3 arası düşüş
            opportunity_score += abs(change_1h)
            opportunity_type = "1h Düşüş Fırsatı"
            recommendation = "AL"
        
        # 3. 4 saatlik trend analizi
        if change_4h < -10:  # Son 4 saatte %10'dan fazla düşüş
            opportunity_score += 15
            opportunity_type = "4h Aşırı Düşüş Fırsatı"
            recommendation = "ACİL AL"
        
        elif change_4h < -5:  # Son 4 saatte %5-10 arası düşüş
            opportunity_score += 10
            opportunity_type = "4h Düşüş Fırsatı"
            recommendation = "HIZLI AL"
        
        # 4. RSI analizi
        rsi = self.calculate_rsi(df['close'])
        if rsi < 30:  # Aşırı satım bölgesi
            opportunity_score += 20
            opportunity_type = "Aşırı Satım Fırsatı"
            recommendation = "ACİL AL"
        elif rsi < 40:
            opportunity_score += 10
            opportunity_type = "Satım Bölgesi Fırsatı"
            recommendation = "HIZLI AL"
        
        # 5. Hacim artışı kontrolü
        recent_volume = float(df['volume'].iloc[-1:].sum())
        avg_volume = float(df['volume'].iloc[-24:].mean())
        if recent_volume > avg_volume * 1.5:  # Son 1 saatte hacim %50 artmış
            opportunity_score += 10
            opportunity_type = "Hacim Artışı Fırsatı"
            recommendation = "HIZLI AL"
        
        # 6. Fiyat seviyesi kontrolü
        if current_price < 0.01:  # Çok düşük fiyatlı coinler
            opportunity_score += 5
            opportunity_type = "Düşük Fiyat Fırsatı"
        
        # Sonuç
        return {
            'symbol': symbol,
            'current_price': current_price,
            'change_1h': change_1h,
            'change_4h': change_4h,
            'volume_24h': volume_24h,
            'opportunity_score': opportunity_score,
            'opportunity_type': opportunity_type,
            'recommendation': recommendation,
            'rsi': rsi,
            'last_updated': datetime.now().isoformat()
        }
    
    def find_1h_profit_opportunities(self, min_score: float = 35.0, max_results: int = 15) -> List[Dict]:
        """1 saatlik kazanç potansiyeli olan coinleri bulur"""
        try:
            # Tüm USDT çiftlerini al
            usdt_pairs = self.get_all_usdt_pairs()
            
            if not usdt_pairs:
                return []
            
            profit_opportunities = []
            
            # İlk 100 coin'i analiz et
            pairs_to_analyze = usdt_pairs[:100]
            
            self.logger.info(f"{len(pairs_to_analyze)} coin 1 saatlik kazanç potansiyeli için analiz ediliyor...")
            
            for i, symbol in enumerate(pairs_to_analyze):
                try:
                    # Rate limiting
                    if i % 10 == 0 and i > 0:
                        time.sleep(0.5)
                    
                    # Coin verisini al
                    coin_data = self.get_coin_data(symbol)
                    
                    if coin_data:
                        # 1 saatlik kazanç potansiyeli analizi
                        profit_analysis = self.analyze_1h_profit_potential(coin_data)
                        
                        if profit_analysis and profit_analysis.get('opportunity_score', 0) >= min_score:
                            profit_opportunities.append(profit_analysis)
                    
                except Exception as e:
                    self.logger.error(f"{symbol} 1 saatlik analiz edilirken hata: {e}")
                    continue
            
            # Skora göre sırala
            profit_opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            self.logger.info(f"{len(profit_opportunities)} 1 saatlik kazanç fırsatı bulundu")
            
            return profit_opportunities[:max_results]
            
        except Exception as e:
            self.logger.error(f"1 saatlik kazanç fırsatı arama hatası: {e}")
            return []
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence) hesaplar"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            return macd_line, signal_line
        except Exception as e:
            self.logger.error(f"MACD hesaplama hatası: {e}")
            return pd.Series(), pd.Series()
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands hesaplar"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            return upper_band, sma, lower_band
        except Exception as e:
            self.logger.error(f"Bollinger Bands hesaplama hatası: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """RSI (Relative Strength Index) hesaplar"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50.0  # Varsayılan değer
    
    def find_opportunities(self, min_score: float = 10.0, max_results: int = 20) -> List[Dict]:
        """Fırsat coinlerini bulur"""
        try:
            # Tüm USDT çiftlerini al
            usdt_pairs = self.get_all_usdt_pairs()
            
            if not usdt_pairs:
                return []
            
            opportunities = []
            
            # İlk 100 coin'i analiz et (performans için)
            pairs_to_analyze = usdt_pairs[:100]
            
            self.logger.info(f"{len(pairs_to_analyze)} coin analiz ediliyor...")
            
            for i, symbol in enumerate(pairs_to_analyze):
                try:
                    # Rate limiting
                    if i % 10 == 0 and i > 0:
                        time.sleep(0.5)
                    
                    # Coin verisini al
                    coin_data = self.get_coin_data(symbol)
                    
                    if coin_data:
                        # Fırsat analizi yap
                        opportunity = self.analyze_coin_opportunity(coin_data)
                        
                        if opportunity and opportunity.get('opportunity_score', 0) >= min_score:
                            opportunities.append(opportunity)
                    
                except Exception as e:
                    self.logger.error(f"{symbol} analiz edilirken hata: {e}")
                    continue
            
            # Skora göre sırala
            opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            self.logger.info(f"{len(opportunities)} fırsat bulundu")
            
            return opportunities[:max_results]
            
        except Exception as e:
            self.logger.error(f"Fırsat arama hatası: {e}")
            return []
    
    def get_coin_details(self, symbol: str) -> Dict:
        """Coin'in detaylı bilgilerini getirir"""
        try:
            # Temel veri
            coin_data = self.get_coin_data(symbol)
            if not coin_data:
                return {}
            
            # Ticker bilgisi
            ticker_info = self.get_ticker_info(symbol)
            
            # Fırsat analizi
            opportunity = self.analyze_coin_opportunity(coin_data)
            
            # Teknik analiz
            df = coin_data['data']
            rsi = self.calculate_rsi(df['close'])
            
            # Destek/Direnç seviyeleri
            high_24h = df['high'].iloc[-24:].max()
            low_24h = df['low'].iloc[-24:].min()
            
            return {
                'symbol': symbol,
                'current_price': coin_data['current_price'],
                'change_24h': coin_data['change_24h'],
                'change_7d': coin_data['change_7d'],
                'volume_24h': coin_data['volume_24h'],
                'high_24h': high_24h,
                'low_24h': low_24h,
                'rsi': rsi,
                'opportunity': opportunity,
                'ticker_info': ticker_info,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"{symbol} detayları alınırken hata: {e}")
            return {}
    
    def get_chart_data(self, symbol: str, interval: str = "1h", limit: int = 168) -> Optional[pd.DataFrame]:
        """Coin'in grafik verilerini getirir"""
        try:
            coin_data = self.get_coin_data(symbol, interval, limit)
            if coin_data and 'data' in coin_data:
                return coin_data['data']
            return None
        except Exception as e:
            self.logger.error(f"{symbol} grafik verisi alınırken hata: {e}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Teknik analiz göstergelerini hesaplar"""
        try:
            if df.empty:
                return {}
            
            close_prices = df['close']
            high_prices = df['high']
            low_prices = df['low']
            volume = df['volume']
            
            # RSI
            rsi = self.calculate_rsi(close_prices)
            
            # SMA (Simple Moving Average)
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            
            # EMA (Exponential Moving Average)
            ema_12 = close_prices.ewm(span=12).mean().iloc[-1]
            ema_26 = close_prices.ewm(span=26).mean().iloc[-1]
            
            # MACD
            macd_line = float(ema_12 - ema_26)
            signal_line = float((close_prices.ewm(span=12).mean() - close_prices.ewm(span=26).mean()).ewm(span=9).mean().iloc[-1])
            macd_histogram = macd_line - signal_line
            
            # Bollinger Bands
            bb_period = 20
            bb_std = 2
            bb_sma = close_prices.rolling(window=bb_period).mean()
            bb_std_dev = close_prices.rolling(window=bb_period).std()
            bb_upper = bb_sma + (bb_std_dev * bb_std)
            bb_lower = bb_sma - (bb_std_dev * bb_std)
            
            current_price = close_prices.iloc[-1]
            bb_upper_current = bb_upper.iloc[-1]
            bb_lower_current = bb_lower.iloc[-1]
            
            # Stochastic RSI
            stoch_rsi = self.calculate_stochastic_rsi(close_prices)
            
            return {
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'ema_12': ema_12,
                'ema_26': ema_26,
                'macd_line': macd_line,
                'macd_signal': signal_line,
                'macd_histogram': macd_histogram,
                'bb_upper': bb_upper_current,
                'bb_lower': bb_lower_current,
                'bb_middle': bb_sma.iloc[-1],
                'stoch_rsi': stoch_rsi,
                'current_price': current_price
            }
            
        except Exception as e:
            self.logger.error(f"Teknik göstergeler hesaplanırken hata: {e}")
            return {}
    
    def calculate_stochastic_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Stochastic RSI hesaplar"""
        try:
            rsi = self.calculate_rsi(prices, period)
            rsi_series = pd.Series([rsi] * len(prices))  # Basit yaklaşım
            
            # Stochastic hesaplama
            rsi_min = rsi_series.rolling(window=period).min()
            rsi_max = rsi_series.rolling(window=period).max()
            
            if rsi_max.iloc[-1] - rsi_min.iloc[-1] != 0:
                stoch_rsi = (rsi - rsi_min.iloc[-1]) / (rsi_max.iloc[-1] - rsi_min.iloc[-1])
                return float(stoch_rsi)
            else:
                return 0.5
        except:
            return 0.5 