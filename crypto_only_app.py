#!/usr/bin/env python3
"""
Crypto Analiz ve Alım-Satım Uygulaması
Basit ve çalışan versiyon
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import warnings
import logging
import os
import sys
warnings.filterwarnings('ignore')

# Proje modüllerini import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Crypto analiz modülü
from crypto.crypto_analyzer import CryptoAnalyzer

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Crypto Analiz ve Trading",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .opportunity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlatma
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []
    print(f"DEBUG: Watchlist başlatıldı: {st.session_state['watchlist']}")

if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = {}

if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

if "user_balance" not in st.session_state:
    st.session_state["user_balance"] = 1000000.0  # 1 milyon TL

if "opportunities_data" not in st.session_state:
    st.session_state["opportunities_data"] = None

if "crypto_analyzer" not in st.session_state:
    st.session_state["crypto_analyzer"] = CryptoAnalyzer()

if "refresh_watchlist" not in st.session_state:
    st.session_state["refresh_watchlist"] = False

# Exchange rate service
class ExchangeRateService:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 dakika
    
    def get_usdt_try_rate(self):
        """USDT/TRY kurunu al"""
        current_time = time.time()
        
        # Cache kontrolü
        if 'usdt_try' in self.cache and current_time - self.cache_time.get('usdt_try', 0) < self.cache_duration:
            return self.cache['usdt_try']
        
        try:
            # Binance API'den USDT/TRY kuru
            response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=USDTTUSD')
            if response.status_code == 200:
                usdt_usd = float(response.json()['price'])
                
                # USD/TRY kuru için alternatif API
                try:
                    response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                    if response.status_code == 200:
                        usd_try = response.json()['rates']['TRY']
                        usdt_try = usdt_usd * usd_try
                        
                        # Cache'e kaydet
                        self.cache['usdt_try'] = usdt_try
                        self.cache_time['usdt_try'] = current_time
                        
                        print(f"INFO: Güncel USDT/TRY kuru: {usdt_try:.4f}")
                        return usdt_try
                except Exception as e:
                    print(f"WARNING: Exchange rate API hatası: {e}")
                
                # Fallback: Sabit kur
                usdt_try = 40.0
                self.cache['usdt_try'] = usdt_try
                self.cache_time['usdt_try'] = current_time
                print(f"INFO: Varsayılan USDT/TRY kuru kullanılıyor: {usdt_try:.4f}")
                return usdt_try
        except Exception as e:
            print(f"ERROR: Döviz kuru alınamadı: {e}")
            # Fallback: Sabit kur
            usdt_try = 40.0
            self.cache['usdt_try'] = usdt_try
            self.cache_time['usdt_try'] = current_time
            print(f"INFO: Varsayılan USDT/TRY kuru kullanılıyor: {usdt_try:.4f}")
            return usdt_try

# Exchange rate service'i başlat
exchange_rate_service = ExchangeRateService()

# Callback fonksiyonları
def add_to_watchlist_callback(symbol):
    """Callback fonksiyonu - watchlist'e ekle"""
    def callback():
        add_to_watchlist(symbol)
    return callback

def remove_from_watchlist_callback(symbol):
    """Callback fonksiyonu - watchlist'ten çıkar"""
    def callback():
        remove_from_watchlist(symbol)
    return callback

# Fonksiyonlar
def add_to_watchlist(symbol):
    """Takip listesine ekle"""
    print(f"DEBUG: add_to_watchlist çağrıldı: {symbol}")
    
    if symbol not in st.session_state["watchlist"]:
        st.session_state["watchlist"].append(symbol)
        print(f"DEBUG: {symbol} takip listesine eklendi")
        print(f"INFO: {symbol} takip listesine eklendi")
        st.success(f"✅ {symbol} takip listesine eklendi!")
        return True
    else:
        print(f"DEBUG: {symbol} zaten takip listesinde")
        st.warning(f"⚠️ {symbol} zaten takip listesinde!")
        return False

def remove_from_watchlist(symbol):
    """Takip listesinden çıkar"""
    if symbol in st.session_state["watchlist"]:
        st.session_state["watchlist"].remove(symbol)
        st.success(f"❌ {symbol} takip listesinden çıkarıldı!")
        print(f"DEBUG: {symbol} watchlist'ten çıkarıldı. Güncel liste: {st.session_state['watchlist']}")
        return True
    else:
        st.warning(f"⚠️ {symbol} takip listesinde bulunamadı!")
        return False

def buy_crypto(symbol, amount_usdt, price):
    """Crypto satın al"""
    exchange_rate = exchange_rate_service.get_usdt_try_rate()
    amount_try = amount_usdt * exchange_rate
    
    if st.session_state["user_balance"] >= amount_try:
        st.session_state["user_balance"] -= amount_try
        
        if symbol not in st.session_state["portfolio"]:
            st.session_state["portfolio"][symbol] = {'amount': 0, 'avg_price': 0}
        
        current_amount = st.session_state["portfolio"][symbol]['amount']
        current_avg_price = st.session_state["portfolio"][symbol]['avg_price']
        
        new_amount = current_amount + amount_usdt
        new_avg_price = ((current_amount * current_avg_price) + (amount_usdt * price)) / new_amount
        
        st.session_state["portfolio"][symbol] = {
            'amount': new_amount,
            'avg_price': new_avg_price
        }
        
        # İşlem geçmişine ekle
        transaction = {
            'timestamp': datetime.now(),
            'type': 'BUY',
            'symbol': symbol,
            'amount': amount_usdt,
            'price': price,
            'total_try': amount_try
        }
        st.session_state["transactions"].append(transaction)
        
        print(f"INFO: {amount_usdt} {symbol} satın alındı: {amount_try:.2f} TL")
        return True
    else:
        print(f"ERROR: Yetersiz bakiye. Gerekli: {amount_try:.2f} TL, Mevcut: {st.session_state['user_balance']:.2f} TL")
        return False

def sell_crypto(symbol, amount_usdt, price):
    """Crypto sat"""
    if symbol in st.session_state["portfolio"] and st.session_state["portfolio"][symbol]['amount'] >= amount_usdt:
        exchange_rate = exchange_rate_service.get_usdt_try_rate()
        amount_try = amount_usdt * exchange_rate
        
        st.session_state["user_balance"] += amount_try
        st.session_state["portfolio"][symbol]['amount'] -= amount_usdt
        
        if st.session_state["portfolio"][symbol]['amount'] <= 0:
            del st.session_state["portfolio"][symbol]
        
        # İşlem geçmişine ekle
        transaction = {
            'timestamp': datetime.now(),
            'type': 'SELL',
            'symbol': symbol,
            'amount': amount_usdt,
            'price': price,
            'total_try': amount_try
        }
        st.session_state["transactions"].append(transaction)
        
        print(f"INFO: {amount_usdt} {symbol} satıldı: {amount_try:.2f} TL")
        return True
    else:
        print(f"ERROR: Yetersiz {symbol} miktarı")
        return False

def filter_opportunities_by_category(opportunities, category):
    """Fırsatları kategoriye göre filtrele"""
    if category == "ALL":
        return opportunities
    
    # Kategori filtreleme mantığı
    filtered = []
    for opp in opportunities:
        symbol = opp['symbol']
        
        if category == "MAJOR" and any(major in symbol for major in ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']):
            filtered.append(opp)
        elif category == "ALTCOIN" and not any(major in symbol for major in ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']):
            filtered.append(opp)
        elif category == "MEME" and any(meme in symbol for meme in ['DOGE', 'SHIB', 'PEPE', 'FLOKI']):
            filtered.append(opp)
        elif category == "DEFI" and any(defi in symbol for defi in ['UNI', 'AAVE', 'COMP', 'MKR']):
            filtered.append(opp)
        elif category == "GAMING" and any(gaming in symbol for gaming in ['AXS', 'MANA', 'SAND', 'ENJ']):
            filtered.append(opp)
        elif category == "LAYER1" and any(layer1 in symbol for layer1 in ['AVAX', 'MATIC', 'ATOM', 'NEAR']):
            filtered.append(opp)
        elif category == "LAYER2" and any(layer2 in symbol for layer2 in ['ARB', 'OP', 'IMX']):
            filtered.append(opp)
        elif category == "AI" and any(ai in symbol for ai in ['FET', 'OCEAN', 'AGIX', 'RNDR']):
            filtered.append(opp)
        elif category == "EXCHANGE" and any(exchange in symbol for exchange in ['BNB', 'OKB', 'HT', 'KCS']):
            filtered.append(opp)
        elif category == "UTILITY" and any(utility in symbol for utility in ['LINK', 'BAT', 'ZRX']):
            filtered.append(opp)
        elif category == "MICRO_CAP" and opp.get('volume_24h', 0) < 10000000:  # 10M USDT altı
            filtered.append(opp)
    
    return filtered

def determine_coin_type(symbol, price, volume):
    """Coin'in türünü belirler"""
    
    # Major coins (ana coinler)
    major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'BCHUSDT']
    
    # Stablecoins (sabit coinler)
    stablecoins = ['USDTUSDT', 'USDCUSDT', 'BUSDUSDT', 'DAIUSDT', 'TUSDUSDT', 'FRAXUSDT']
    
    # Meme coins (meme coinler) - genellikle düşük fiyatlı ve yüksek hacimli
    meme_indicators = ['DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'MYRO', 'POPCAT', 'BOOK', 'TURBO']
    
    # DeFi tokens (DeFi tokenleri)
    defi_indicators = ['UNI', 'AAVE', 'COMP', 'MKR', 'SUSHI', 'CRV', 'BAL', 'YFI', 'SNX', '1INCH']
    
    # Gaming tokens (oyun tokenleri)
    gaming_indicators = ['AXS', 'MANA', 'SAND', 'ENJ', 'GALA', 'ILV', 'ALICE', 'HERO', 'TLM', 'ALPHA']
    
    # Layer 1 coins (katman 1 coinler)
    layer1_indicators = ['AVAX', 'MATIC', 'ATOM', 'NEAR', 'FTM', 'ALGO', 'ICP', 'APT', 'SUI', 'SEI']
    
    # Layer 2 coins (katman 2 coinler)
    layer2_indicators = ['ARB', 'OP', 'IMX', 'ZKSYNC', 'STARK', 'POLYGON', 'OPTIMISM']
    
    # AI tokens (yapay zeka tokenleri)
    ai_indicators = ['FET', 'OCEAN', 'AGIX', 'RNDR', 'TAO', 'BITTENSOR', 'AI', 'GPT', 'NEURAL']
    
    # Exchange tokens (borsa tokenleri)
    exchange_indicators = ['BNB', 'OKB', 'HT', 'KCS', 'GT', 'MX', 'BGB', 'CRO', 'FTT']
    
    # Utility tokens (fayda tokenleri)
    utility_indicators = ['LINK', 'CHAINLINK', 'BAT', 'ZRX', 'REP', 'KNC', 'BAND', 'API3']
    
    # Coin türünü belirle
    if symbol in major_coins:
        return "Major Coin"
    elif symbol in stablecoins:
        return "Stablecoin"
    elif any(meme in symbol for meme in meme_indicators):
        return "Meme Coin"
    elif any(defi in symbol for defi in defi_indicators):
        return "DeFi Token"
    elif any(gaming in symbol for gaming in gaming_indicators):
        return "Gaming Token"
    elif any(layer1 in symbol for layer1 in layer1_indicators):
        return "Layer 1"
    elif any(layer2 in symbol for layer2 in layer2_indicators):
        return "Layer 2"
    elif any(ai in symbol for ai in ai_indicators):
        return "AI Token"
    elif any(exchange in symbol for exchange in exchange_indicators):
        return "Exchange Token"
    elif any(utility in symbol for utility in utility_indicators):
        return "Utility Token"
    elif price < 0.01:
        return "Micro Cap"
    elif volume < 1000000:
        return "Low Volume"
    else:
        return "Altcoin"

# Ana uygulama
def main():
    st.title("🪙 Crypto Analiz ve Trading")
    st.markdown("**Basit ve çalışan crypto analiz sistemi**")
    
    # Sidebar
    st.sidebar.header("💰 Bakiye")
    st.metric("TL Bakiye", f"{st.session_state['user_balance']:,.2f} TL")
    
    # Güncel döviz kuru
    exchange_rate = exchange_rate_service.get_usdt_try_rate()
    if exchange_rate is not None:
        st.sidebar.info(f"💱 **Güncel Döviz Kuru:** 1 USDT = {exchange_rate:.4f} TL")
    else:
        st.sidebar.info("💱 **Güncel Döviz Kuru:** 1 USDT = 40.0000 TL (Varsayılan)")
        exchange_rate = 40.0
    
    # Takip listesi
    st.sidebar.header("👀 Takip Listesi")
    if st.session_state["watchlist"]:
        st.sidebar.write(f"📋 **{len(st.session_state['watchlist'])} coin takip ediliyor**")
        for symbol in st.session_state["watchlist"]:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.sidebar.write(f"📈 {symbol}")
            with col2:
                if st.sidebar.button("❌", key=f"remove_{symbol}", on_click=remove_from_watchlist_callback(symbol)):
                    print(f"DEBUG: {symbol} watchlist'ten çıkarıldı")
    else:
        st.sidebar.info("📝 Takip listesi boş")
    
    # Crypto analyzer'ı al
    crypto_analyzer = st.session_state["crypto_analyzer"]
    
    # Coin türleri tanımla
    coin_categories = {
        "Tüm Coinler": "ALL",
        "Major Coinler": "MAJOR",
        "Altcoinler": "ALTCOIN", 
        "Meme Coinler": "MEME",
        "DeFi Tokenleri": "DEFI",
        "Gaming Tokenleri": "GAMING",
        "Layer 1 Coinler": "LAYER1",
        "Layer 2 Coinler": "LAYER2",
        "AI Tokenleri": "AI",
        "Exchange Tokenleri": "EXCHANGE",
        "Utility Tokenleri": "UTILITY",
        "Micro Cap Coinler": "MICRO_CAP"
    }
    
    # Sekmeler
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Fırsat Analizi", "💰 24h Kazanç Analizi", "📊 Coin Detayları", "📈 Grafik Analizi", "⚙️ Ayarlar"])
    
    with tab1:
        st.subheader("🚀 Crypto Fırsat Analizi")
        st.markdown("**Düşüş gösteren ve artış potansiyeli olan coinleri tespit eder**")
        
        # Analiz parametreleri
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            min_score = st.slider("Minimum Fırsat Skoru:", 5, 50, 15, key="crypto_min_score")
        
        with col2:
            max_results = st.slider("Maksimum Sonuç:", 5, 50, 15, key="crypto_max_results")
        
        with col3:
            min_volume = st.number_input("Min. Hacim (Milyon USDT):", 1, 100, 10, key="crypto_min_volume")
        
        with col4:
            selected_category = st.selectbox("Coin Türü:", list(coin_categories.keys()), key="crypto_category")
        
        # Coin türü açıklaması
        category_descriptions = {
            "Tüm Coinler": "Tüm kategorilerdeki coinler analiz edilir",
            "Major Coinler": "Bitcoin, Ethereum, BNB gibi büyük coinler",
            "Altcoinler": "Düşük fiyatlı alternatif coinler",
            "Meme Coinler": "DOGE, SHIB, PEPE gibi meme coinler",
            "DeFi Tokenleri": "Merkeziyetsiz finans protokolleri",
            "Gaming Tokenleri": "Oyun ve metaverse tokenleri",
            "Layer 1 Coinler": "Ana blockchain platformları",
            "Layer 2 Coinler": "Ölçeklendirme çözümleri",
            "AI Tokenleri": "Yapay zeka projeleri",
            "Exchange Tokenleri": "Borsa tokenleri",
            "Utility Tokenleri": "Fayda tokenleri",
            "Micro Cap Coinler": "Düşük piyasa değerli coinler"
        }
        
        st.info(f"📋 **Seçilen Kategori:** {selected_category} - {category_descriptions[selected_category]}")
        
        if st.button("🔍 Crypto Fırsatlarını Analiz Et", type="primary", key="analyze_crypto_opportunities"):
            print(f"DEBUG CRYPTO: Crypto Fırsatlarını Analiz Et butonuna tıklandı!")
            with st.spinner("🔄 Crypto fırsatları analiz ediliyor..."):
                try:
                    # Crypto analyzer parametrelerini güncelle
                    crypto_analyzer.min_volume_usdt = min_volume * 1000000
                    
                    # Fırsatları bul
                    opportunities = crypto_analyzer.find_opportunities(min_score=min_score, max_results=max_results)
                    
                    if opportunities:
                        # Coin türüne göre filtrele
                        filtered_opportunities = filter_opportunities_by_category(opportunities, coin_categories[selected_category])
                        
                        if filtered_opportunities:
                            st.success(f"✅ {len(filtered_opportunities)} {selected_category.lower()} fırsatı bulundu!")
                            
                            # Fırsatları göster
                            st.subheader(f"🔥 {selected_category} Fırsatları")
                            
                            for i, opportunity in enumerate(filtered_opportunities):
                                # Tavsiye rengi belirleme
                                if opportunity['recommendation'] == "KESİNLİKLE AL":
                                    recommendation_color = "🟢"
                                    bg_color = "background-color: #d4edda; border-left: 4px solid #28a745;"
                                elif opportunity['recommendation'] == "GÜÇLÜ AL":
                                    recommendation_color = "🟡"
                                    bg_color = "background-color: #fff3cd; border-left: 4px solid #ffc107;"
                                elif opportunity['recommendation'] == "AL":
                                    recommendation_color = "🟠"
                                    bg_color = "background-color: #f8d7da; border-left: 4px solid #dc3545;"
                                else:
                                    recommendation_color = "⚪"
                                    bg_color = "background-color: #f8f9fa; border-left: 4px solid #6c757d;"
                                
                                st.markdown(f"""
                                <div style="{bg_color} padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                                    <h4>{recommendation_color} {opportunity['symbol']} - {opportunity['recommendation']}</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                                
                                with col1:
                                    coin_type = determine_coin_type(opportunity['symbol'], opportunity['current_price'], opportunity['volume_24h'])
                                    st.write(f"**Coin Türü:** {coin_type}")
                                    st.write(f"💰 **Güncel Fiyat:** ${opportunity['current_price']:.6f}")
                                    st.write(f"📊 **24h Değişim:** {opportunity['change_24h']:+.2f}%")
                                    st.write(f"📈 **7g Değişim:** {opportunity['change_7d']:+.2f}%")
                                
                                with col2:
                                    st.metric("Skor", f"{opportunity['opportunity_score']:.1f}")
                                    if opportunity.get('rsi'):
                                        st.metric("RSI", f"{opportunity['rsi']:.1f}")
                                
                                with col3:
                                    st.metric("Hacim", f"${opportunity['volume_24h']/1000000:.1f}M")
                                    st.metric("Öneri", opportunity['recommendation'])
                                
                                with col4:
                                    # Takibe Al butonu - Basit ve çalışan
                                    st.write(f"🔴 DEBUG: {opportunity['symbol']} için buton oluşturuluyor")
                                    st.write(f"🔴 DEBUG: Buton key: crypto_watch_{opportunity['symbol']}_{i}")
                                
                                # Callback ile buton
                                button_key = f"crypto_watch_{opportunity['symbol']}_{i}"
                                st.write(f"🔴 DEBUG: Buton key: {button_key}")
                                
                                if st.button(f"📈 {opportunity['symbol']} TAKIBE AL", key=button_key, on_click=add_to_watchlist_callback(opportunity['symbol'])):
                                    print(f"DEBUG CRYPTO: Takibe Al butonuna tıklandı: {opportunity['symbol']}")
                                else:
                                    st.write(f"🔴 DEBUG: {opportunity['symbol']} butonu tıklanmadı")
                                
                                st.divider()
                            
                            # Özet istatistikler
                            st.subheader("📊 Fırsat Özeti")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Toplam Fırsat", len(filtered_opportunities))
                            
                            with col2:
                                avg_score = sum(opp['opportunity_score'] for opp in filtered_opportunities) / len(filtered_opportunities)
                                st.metric("Ortalama Skor", f"{avg_score:.1f}")
                            
                            with col3:
                                best_opportunity = max(filtered_opportunities, key=lambda x: x['opportunity_score'])
                                st.metric("En İyi Fırsat", best_opportunity['symbol'])
                            
                            with col4:
                                avg_drop = sum(opp['change_7d'] for opp in filtered_opportunities) / len(filtered_opportunities)
                                st.metric("Ortalama Düşüş", f"{avg_drop:.1f}%")
                        
                        else:
                            st.warning(f"❌ {selected_category} kategorisinde fırsat bulunamadı.")
                            st.info("💡 Farklı bir kategori seçin veya parametreleri değiştirin.")
                    
                    else:
                        st.warning("❌ Belirtilen kriterlere uygun crypto fırsatı bulunamadı.")
                        st.info("💡 Daha düşük bir minimum skor deneyin.")
                
                except Exception as e:
                    st.error(f"Crypto analizi sırasında hata oluştu: {str(e)}")
    
    with tab2:
        st.subheader("💰 24 Saatlik Kazanç Analizi")
        st.markdown("**Uzun süredir düşüşte olan ama 24 saat içinde artış potansiyeli olan coinleri tespit eder**")
        
        # Analiz parametreleri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_profit_score = st.slider("Minimum Kazanç Skoru:", 15, 80, 25, key="profit_min_score")
        
        with col2:
            max_profit_results = st.slider("Maksimum Sonuç:", 5, 30, 10, key="profit_max_results")
        
        with col3:
            selected_profit_category = st.selectbox("Coin Türü:", list(coin_categories.keys()), key="profit_category")
        
        st.info(f"📋 **24 Saatlik Analiz:** {selected_profit_category} kategorisinde uzun düşüşten sonra artış potansiyeli olan {min_profit_score}+ skorlu coinler")
        
        if st.button("💰 24 Saatlik Kazanç Fırsatlarını Analiz Et", type="primary", key="analyze_24h_profit"):
            print(f"DEBUG CRYPTO: 24 Saatlik Kazanç Fırsatlarını Analiz Et butonuna tıklandı!")
            with st.spinner("🔄 24 saatlik kazanç fırsatları analiz ediliyor..."):
                try:
                    # 24 saatlik kazanç fırsatlarını bul
                    profit_opportunities = crypto_analyzer.find_24h_profit_opportunities(min_score=min_profit_score, max_results=max_profit_results)
                    
                    if profit_opportunities:
                        print(f"DEBUG: {len(profit_opportunities)} fırsat bulundu")
                        # Coin türüne göre filtrele
                        filtered_profit_opportunities = filter_opportunities_by_category(profit_opportunities, coin_categories[selected_profit_category])
                        print(f"DEBUG: Filtreleme sonrası {len(filtered_profit_opportunities)} fırsat kaldı")
                        
                        # Session state'e kaydet
                        st.session_state["opportunities_data"] = filtered_profit_opportunities
                        print(f"🔴🔴🔴 DEBUG: opportunities_data session state'e kaydedildi: {len(filtered_profit_opportunities)} fırsat 🔴🔴🔴")
                        
                        if filtered_profit_opportunities:
                            st.success(f"✅ {len(filtered_profit_opportunities)} {selected_profit_category.lower()} 24 saatlik kazanç fırsatı bulundu!")
                            
                            # Fırsatları göster
                            st.subheader(f"🔥 24 Saatlik Kazanç Fırsatları")
                            
                            for i, opportunity in enumerate(filtered_profit_opportunities):
                                # Tavsiye rengi belirleme
                                if opportunity['recommendation'] == "KESİNLİKLE AL":
                                    recommendation_color = "🟢"
                                    bg_color = "background-color: #d4edda; border-left: 4px solid #28a745;"
                                elif opportunity['recommendation'] == "GÜÇLÜ AL":
                                    recommendation_color = "🟡"
                                    bg_color = "background-color: #fff3cd; border-left: 4px solid #ffc107;"
                                elif opportunity['recommendation'] == "AL":
                                    recommendation_color = "🟠"
                                    bg_color = "background-color: #f8d7da; border-left: 4px solid #dc3545;"
                                else:
                                    recommendation_color = "⚪"
                                    bg_color = "background-color: #f8f9fa; border-left: 4px solid #6c757d;"
                                
                                st.markdown(f"""
                                <div style="{bg_color} padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                                    <h4>{recommendation_color} {opportunity['symbol']} - {opportunity['recommendation']}</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                                
                                with col1:
                                    coin_type = determine_coin_type(opportunity['symbol'], opportunity['current_price'], opportunity['volume_24h'])
                                    st.write(f"**Coin Türü:** {coin_type}")
                                    st.write(f"💰 **Güncel Fiyat:** ${opportunity['current_price']:.6f}")
                                    st.write(f"🎯 **Hedef Fiyat:** ${opportunity['target_price']:.6f}")
                                    st.write(f"📈 **Potansiyel Kazanç:** {opportunity['potential_gain_percent']:+.2f}%")
                                
                                with col2:
                                    st.metric("Kazanç Skoru", f"{opportunity['profit_score']:.1f}")
                                    st.metric("Güven", opportunity['confidence'])
                                
                                with col3:
                                    st.metric("24h Değişim", f"{opportunity['change_24h']:+.2f}%")
                                    st.metric("7g Değişim", f"{opportunity['change_7d']:+.2f}%")
                                
                                with col4:
                                    # Takibe Al butonu - Basit ve çalışan
                                    st.write(f"🔴 DEBUG: {opportunity['symbol']} için buton oluşturuluyor")
                                    st.write(f"🔴 DEBUG: Buton key: profit_watch_{opportunity['symbol']}_{i}")
                                
                                # Callback ile buton
                                button_key = f"profit_watch_{opportunity['symbol']}_{i}"
                                st.write(f"🔴 DEBUG: Buton key: {button_key}")
                                
                                if st.button(f"📈 {opportunity['symbol']} TAKIBE AL", key=button_key, on_click=add_to_watchlist_callback(opportunity['symbol'])):
                                    print(f"DEBUG CRYPTO: Takibe Al butonuna tıklandı: {opportunity['symbol']}")
                                else:
                                    st.write(f"🔴 DEBUG: {opportunity['symbol']} butonu tıklanmadı")
                                
                                # Özel durum göstergeleri
                                col_status1, col_status2 = st.columns(2)
                                with col_status1:
                                    if opportunity.get('long_term_drop', False):
                                        st.success("📉 Uzun vadeli düşüş tespit edildi")
                                    if opportunity.get('recovery_started', False):
                                        st.success("📈 Toparlanma başladı")
                                
                                with col_status2:
                                    st.metric("RSI", f"{opportunity['rsi']:.1f}")
                                    st.metric("Hacim", f"${opportunity['volume_24h']/1000000:.1f}M")
                                
                                # Sebepler
                                if opportunity['reasoning']:
                                    st.write("**📊 Analiz Sebepleri:**")
                                    for reason in opportunity['reasoning']:
                                        st.write(f"• {reason}")
                                
                                st.divider()
                            
                            # Özet istatistikler
                            st.subheader("📊 24 Saatlik Kazanç Özeti")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Toplam Fırsat", len(filtered_profit_opportunities))
                            
                            with col2:
                                avg_profit_score = sum(opp['profit_score'] for opp in filtered_profit_opportunities) / len(filtered_profit_opportunities)
                                st.metric("Ortalama Skor", f"{avg_profit_score:.1f}")
                            
                            with col3:
                                best_profit_opportunity = max(filtered_profit_opportunities, key=lambda x: x['profit_score'])
                                st.metric("En İyi Fırsat", best_profit_opportunity['symbol'])
                            
                            with col4:
                                avg_potential_gain = sum(opp['potential_gain_percent'] for opp in filtered_profit_opportunities) / len(filtered_profit_opportunities)
                                st.metric("Ortalama Potansiyel", f"{avg_potential_gain:+.1f}%")
                            
                            # Özel kategoriler
                            st.subheader("🎯 Özel Kategoriler")
                            col_cat1, col_cat2, col_cat3 = st.columns(3)
                            
                            with col_cat1:
                                kesinlikle_al_count = sum(1 for opp in filtered_profit_opportunities if opp['recommendation'] == "KESİNLİKLE AL")
                                st.metric("KESİNLİKLE AL", kesinlikle_al_count)
                            
                            with col_cat2:
                                guclu_al_count = sum(1 for opp in filtered_profit_opportunities if opp['recommendation'] == "GÜÇLÜ AL")
                                st.metric("GÜÇLÜ AL", guclu_al_count)
                            
                            with col_cat3:
                                recovery_count = sum(1 for opp in filtered_profit_opportunities if opp.get('recovery_started', False))
                                st.metric("Toparlanma Başladı", recovery_count)
                        
                        else:
                            st.warning(f"❌ {selected_profit_category} kategorisinde 24 saatlik kazanç fırsatı bulunamadı.")
                            st.info("💡 Farklı bir kategori seçin veya skoru düşürün.")
                    
                    else:
                        st.warning("❌ 24 saatlik kazanç fırsatı bulunamadı.")
                        st.info("💡 Daha düşük bir minimum skor deneyin.")
                
                except Exception as e:
                    st.error(f"24 saatlik kazanç analizi sırasında hata oluştu: {str(e)}")
    
    with tab3:
        st.subheader("📊 Coin Detayları")
        
        # Coin seçimi
        col1, col2 = st.columns(2)
        
        with col1:
            # Popüler coinler listesi
            popular_coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", 
                           "DOTUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT", "XRPUSDT"]
            selected_coin = st.selectbox("Coin Seçin:", popular_coins, key="crypto_coin_select")
        
        with col2:
            if st.button("🔍 Coin Detaylarını Getir", key="get_coin_details"):
                with st.spinner("Coin detayları alınıyor..."):
                    try:
                        coin_details = crypto_analyzer.get_coin_details(selected_coin)
                        
                        if coin_details:
                            st.success(f"✅ {selected_coin} detayları alındı!")
                            
                            # Coin bilgileri
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Güncel Fiyat", f"${coin_details['current_price']:.6f}")
                                st.metric("24h Değişim", f"{coin_details['change_24h']:+.2f}%")
                            
                            with col2:
                                st.metric("7g Değişim", f"{coin_details['change_7d']:+.2f}%")
                                st.metric("24h Hacim", f"${coin_details['volume_24h']/1000000:.1f}M")
                            
                            with col3:
                                st.metric("24h En Yüksek", f"${coin_details['high_24h']:.6f}")
                                st.metric("24h En Düşük", f"${coin_details['low_24h']:.6f}")
                            
                            with col4:
                                st.metric("RSI", f"{coin_details['rsi']:.1f}")
                                if coin_details.get('opportunity'):
                                    st.metric("Fırsat Skoru", f"{coin_details['opportunity']['opportunity_score']:.1f}")
                            
                            # Coin türü
                            coin_type = determine_coin_type(selected_coin, coin_details['current_price'], coin_details['volume_24h'])
                            st.info(f"📋 **Coin Türü:** {coin_type}")
                            
                            # Fırsat analizi
                            if coin_details.get('opportunity'):
                                opportunity = coin_details['opportunity']
                                st.subheader("🎯 Fırsat Analizi")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Fırsat Skoru", f"{opportunity['opportunity_score']:.1f}")
                                    st.metric("Öneri", opportunity['recommendation'])
                                
                                with col2:
                                    st.metric("Fırsat Tipi", opportunity['opportunity_type'])
                                    st.metric("Güven", opportunity['confidence'])
                                
                                with col3:
                                    st.metric("Hedef Fiyat", f"${opportunity['target_price']:.6f}")
                                    st.metric("Potansiyel", f"{opportunity['potential_gain_percent']:+.2f}%")
                                
                                # Sebepler
                                if opportunity.get('reasoning'):
                                    st.write("**📊 Analiz Sebepleri:**")
                                    for reason in opportunity['reasoning']:
                                        st.write(f"• {reason}")
                            
                            # Takibe Al butonu - Callback ile
                            if st.button(f"📈 {selected_coin} Takibe Al", key=f"watch_detail_{selected_coin}", on_click=add_to_watchlist_callback(selected_coin)):
                                print(f"DEBUG CRYPTO: Coin detay takibe al butonuna tıklandı: {selected_coin}")
                        
                        else:
                            st.error(f"❌ {selected_coin} detayları alınamadı.")
                    
                    except Exception as e:
                        st.error(f"Coin detayları alınırken hata oluştu: {str(e)}")
    
    with tab4:
        st.subheader("📈 Grafik Analizi")
        st.info("Grafik analizi özelliği yakında eklenecek...")
    
    with tab5:
        st.subheader("⚙️ Crypto Analiz Ayarları")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Analiz Parametreleri:**")
            st.write(f"• Minimum Hacim: {crypto_analyzer.min_volume_usdt/1000000:.0f}M USDT")
            st.write(f"• Minimum Değişim: %{crypto_analyzer.min_price_change}")
            st.write(f"• Fırsat Eşiği: %{crypto_analyzer.opportunity_threshold}")
            st.write(f"• Cache Süresi: {crypto_analyzer.cache_duration} saniye")
        
        with col2:
            st.write("**Veri Kaynakları:**")
            st.write("• Binance API v3")
            st.write("• 1 saatlik mum verileri")
            st.write("• 7 günlük geçmiş")
            st.write("• Anlık ticker bilgileri")
        
        st.subheader("📋 Coin Kategorileri")
        for category, description in category_descriptions.items():
            st.write(f"• **{category}:** {description}")

if __name__ == "__main__":
    main() 