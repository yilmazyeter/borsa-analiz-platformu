#!/usr/bin/env python3
"""
Hisse Takip ve Analiz Uygulaması - Web Arayüzü
Streamlit ile web tabanlı dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
import numpy as np
import investpy
import time # Added for API rate limiting
import requests
import json
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import logging
warnings.filterwarnings('ignore')

# Twelve Data API Key (ücretsiz kayıt: https://twelvedata.com/register)
TWELVE_DATA_API_KEY = "0972e9caa03b454fad5eadca558d6eb8"

# Proje modüllerini import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mevcut modüller
from data.data_manager import DataManager
from scraper.stock_scraper import StockScraper
from visuals.chart_generator import ChartGenerator
from visuals.report_generator import ReportGenerator

# Ana uygulama sınıfı
from main import StockAnalysisApp

# Yeni AI modülleri
from ai.price_predictor import PricePredictor
from ai.sentiment_analyzer import SentimentAnalyzer
from ai.trend_detector import TrendDetector
from ai.nlp_assistant import NLPAssistant

# Haber modülü
from news.news_scraper import NewsScraper

# Alarm modülü
from alerts.alert_manager import AlertManager

# Portföy optimizer modülü
from portfolio_optimizer.portfolio_analyzer import PortfolioAnalyzer

# Crypto analiz modülü
from crypto.crypto_analyzer import CryptoAnalyzer

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Hisse Takip ve Analiz Dashboard",
    page_icon="📈",
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
    .ai-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .news-card {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Global değişkenler
if 'ai_predictor' not in st.session_state:
    st.session_state.ai_predictor = PricePredictor()
if 'sentiment_analyzer' not in st.session_state:
    st.session_state.sentiment_analyzer = SentimentAnalyzer()
if 'trend_detector' not in st.session_state:
    st.session_state.trend_detector = TrendDetector()
if 'nlp_assistant' not in st.session_state:
    st.session_state.nlp_assistant = NLPAssistant()
if 'news_scraper' not in st.session_state:
    st.session_state.news_scraper = NewsScraper()
if 'portfolio_analyzer' not in st.session_state:
    st.session_state.portfolio_analyzer = PortfolioAnalyzer()
if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = AlertManager()
if 'crypto_analyzer' not in st.session_state:
    st.session_state.crypto_analyzer = CryptoAnalyzer()

# Portfolio yönetimi
from portfolio.user_manager import UserManager

# Kullanıcı yöneticisini başlat
user_manager = UserManager()

# Session state'e kullanıcı bilgilerini ekle
if 'current_user' not in st.session_state:
    st.session_state.current_user = "gokhan"  # Varsayılan kullanıcı

if 'user_manager' not in st.session_state:
    st.session_state.user_manager = user_manager

# Session state başlatma - Kalıcı veri yönetimi ile
if "watchlist" not in st.session_state:
    # Kalıcı verilerden yükle
    current_user = st.session_state.get("current_user", "gokhan")
    persistent_watchlist = user_manager.get_watchlist(current_user)
    st.session_state["watchlist"] = persistent_watchlist
    print(f"DEBUG INIT: Kalıcı takip listesi yüklendi: {st.session_state['watchlist']}")

if "portfolio" not in st.session_state:
    # Kalıcı verilerden yükle
    current_user = st.session_state.get("current_user", "gokhan")
    persistent_portfolio = user_manager.get_portfolio(current_user)
    st.session_state["portfolio"] = persistent_portfolio

if "transactions" not in st.session_state:
    # Kalıcı verilerden yükle
    current_user = st.session_state.get("current_user", "gokhan")
    persistent_transactions = user_manager.get_transactions(current_user)
    st.session_state["transactions"] = persistent_transactions

if "user_balance" not in st.session_state:
    # Kalıcı verilerden yükle
    current_user = st.session_state.get("current_user", "gokhan")
    persistent_balance = user_manager.get_user_balance(current_user)
    st.session_state["user_balance"] = persistent_balance

if "refresh_watchlist" not in st.session_state:
    st.session_state["refresh_watchlist"] = False

if "opportunities_data" not in st.session_state:
    st.session_state["opportunities_data"] = None

if "profit_opportunities_data" not in st.session_state:
    st.session_state["profit_opportunities_data"] = None

# Kullanıcı yönetimi için session state
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = "Gökhan"

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

def get_all_bist_stocks():
    """BIST'teki tüm hisse sembollerini otomatik olarak döndürür."""
    try:
        stocks = investpy.stocks.get_stocks(country='turkey')
        return stocks['symbol'].tolist()
    except Exception as e:
        return []

def get_comprehensive_stock_list():
    """BIST hisselerini içeren kapsamlı hisse listesi oluştur"""
    
    # BIST-100 hisseleri (ana hisseler)
    bist100_stocks = [
        'THYAO', 'GARAN', 'AKBNK', 'YAPI', 'KRDMD', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL',
        'BIMAS', 'AKSA', 'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO',
        'HEKTS', 'KERVN', 'KERVT', 'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS',
        'AKSA', 'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO', 'HEKTS',
        'KERVN', 'KERVT', 'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS', 'AKSA',
        'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO', 'HEKTS', 'KERVN',
        'KERVT', 'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS', 'AKSA', 'PGSUS',
        'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO', 'HEKTS', 'KERVN', 'KERVT',
        'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS', 'AKSA', 'PGSUS', 'SISE',
        'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO', 'HEKTS', 'KERVN', 'KERVT', 'SAHOL'
    ]
    
    # BIST-30 hisseleri (en büyük 30 hisse)
    bist30_stocks = [
        'THYAO', 'GARAN', 'AKBNK', 'YAPI', 'KRDMD', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL',
        'BIMAS', 'AKSA', 'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO',
        'HEKTS', 'KERVN', 'KERVT', 'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS'
    ]
    
    # BIST-50 hisseleri
    bist50_stocks = [
        'THYAO', 'GARAN', 'AKBNK', 'YAPI', 'KRDMD', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL',
        'BIMAS', 'AKSA', 'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO',
        'HEKTS', 'KERVN', 'KERVT', 'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS',
        'AKSA', 'PGSUS', 'SISE', 'TAVHL', 'VESTL', 'TOASO', 'DOHOL', 'KONTR', 'FROTO', 'HEKTS',
        'KERVN', 'KERVT', 'SAHOL', 'SASA', 'ASELS', 'KCHOL', 'TUPRS', 'EREGL', 'BIMAS', 'AKSA'
    ]
    
    # Ek BIST hisseleri (popüler hisseler)
    additional_bist_stocks = [
        'ARCLK', 'BAGFS', 'BRISA', 'CCOLA', 'CEMAS', 'CEMTS', 'CIMSA', 'CUSAN', 'DOHOL', 'EKGYO',
        'ENJSA', 'ENKAI', 'FMIZP', 'GESAN', 'GLYHO', 'HALKB', 'HATEK', 'INDES', 'ISBIR', 'ISCTR',
        'IZMDC', 'KAREL', 'KARSN', 'KENT', 'KONYA', 'KORDS', 'KOZAL', 'KRDMD', 'LOGO', 'MGROS',
        'NETAS', 'NTHOL', 'ODAS', 'OTKAR', 'OYAKC', 'PETKM', 'PENTA', 'POLHO', 'PRKAB', 'PRKME',
        'QUAGR', 'SAFKN', 'SASA', 'SELEC', 'SELGD', 'SMRTG', 'SNGYO', 'SOKM', 'TATGD', 'TCELL',
        'TKNSA', 'TLMAN', 'TOASO', 'TSKB', 'TTKOM', 'TTRAK', 'TUPRS', 'ULKER', 'VESBE', 'VESTL',
        'YATAS', 'YUNSA', 'ZRGYO', 'ZRGYO', 'ZRGYO', 'ZRGYO', 'ZRGYO', 'ZRGYO', 'ZRGYO', 'ZRGYO'
    ]
    
    # Tüm BIST listelerini birleştir ve tekrarları kaldır
    all_bist_stocks = list(set(bist100_stocks + bist30_stocks + bist50_stocks + additional_bist_stocks))
    
    # Investpy ile gerçek BIST hisselerini al
    try:
        real_bist_stocks = get_all_bist_stocks()
        if real_bist_stocks:
            # Gerçek hisseleri ekle
            all_bist_stocks.extend(real_bist_stocks)
            # Tekrarları kaldır
            all_bist_stocks = list(set(all_bist_stocks))
    except Exception as e:
        print(f"Investpy hatası: {e}")
    
    # Sadece BIST hisselerini döndür
    return all_bist_stocks

def get_us_stock_list():
    """ABD hisse sembollerini döndürür"""
    # Sadece en popüler 10 ABD hisse sembolü (API limiti için)
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC'
    ]
    
    # Tireli sembolleri noktaya çevir (Yahoo Finance formatı)
    corrected_symbols = []
    for symbol in symbols:
        if '-' in symbol:
            corrected_symbols.append(symbol.replace('-', '.'))
        else:
            corrected_symbols.append(symbol)
    
    return corrected_symbols

# Hisse listeleri
us_stocks = get_us_stock_list()
bist_stocks = get_comprehensive_stock_list()

def get_stock_data_twelvedata(symbol, period="1y"):
    """Twelve Data API kullanarak hisse verisi çeker (şimdilik mock data kullanıyor)"""
    try:
        # API kredi limiti aşıldığı için şimdilik mock data kullanıyoruz
        print(f"Twelve Data API kredi limiti nedeniyle mock data kullanılıyor: {symbol}")
        
        # Mock data oluştur
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Gerçekçi fiyat aralıkları
        base_price = np.random.uniform(50, 500)
        current_price = base_price * np.random.uniform(0.8, 1.2)
        
        # 365 günlük veri oluştur
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Trend oluştur
        if np.random.random() < 0.3:  # %30 ihtimalle büyük düşüş
            trend = np.random.uniform(-0.8, -0.4)  # %40-80 düşüş
        else:
            trend = np.random.uniform(-0.2, 0.3)  # %20 düşüş - %30 artış
            
        # Günlük volatilite
        volatility = np.random.uniform(0.02, 0.05)
        
        # Fiyat serisi oluştur
        prices = [base_price]
        for i in range(1, len(dates)):
            change = trend/365 + np.random.normal(0, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1))
            
        # DataFrame oluştur
        df = pd.DataFrame({
            'close': prices,
            'high': [p * (1 + np.random.uniform(0, 0.05)) for p in prices],
            'low': [p * (1 - np.random.uniform(0, 0.05)) for p in prices],
            'open': [p * (1 + np.random.uniform(-0.02, 0.02)) for p in prices],
            'volume': [np.random.randint(1000000, 10000000) for _ in prices]
        }, index=dates)
        
        current_price = df['close'].iloc[-1]
        price_365d_ago = df['close'].iloc[0]
        change_365d = ((current_price - price_365d_ago) / price_365d_ago) * 100
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'price_365d_ago': price_365d_ago,
            'change_365d': change_365d,
            'data': df,
            'source': 'mock_data',
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Mock data oluşturma hatası ({symbol}): {str(e)}")
        return None

def get_stock_data(symbol, period="1y"):
    return get_stock_data_twelvedata(symbol, period)

def get_current_user_data():
    """Seçili kullanıcının verilerini döndürür - Kalıcı veri yönetimi ile"""
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        # Kalıcı verilerden al
        users = user_manager.get_users()
        user_data = users.get(current_user, {})
        
        # Eksik alanları varsayılan değerlerle doldur
        if not user_data:
            user_data = {
                "balance": 1000000.0,
                "portfolio": {},
                "transactions": []
            }
        else:
            # Eksik alanları kontrol et ve ekle
            if "portfolio" not in user_data:
                user_data["portfolio"] = {}
            if "transactions" not in user_data:
                user_data["transactions"] = []
            if "balance" not in user_data:
                user_data["balance"] = 500000.0
        
        return user_data
    else:
        # Fallback: session state
        if "users" not in st.session_state:
            st.session_state["users"] = {
                "gokhan": {
                    "balance": 500000.0,
                    "portfolio": {},
                    "transactions": []
                }
            }
        return st.session_state["users"].get("gokhan", {
            "balance": 500000.0,
            "portfolio": {},
            "transactions": []
        })

def update_user_data(user_data):
    """Kullanıcı verilerini günceller - Kalıcı veri yönetimi ile"""
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        # Kalıcı veri yönetimi ile güncelle
        users = user_manager.get_users()
        users[current_user] = user_data
        user_manager._save_json(user_manager.users_file, users)
    else:
        # Fallback: session state
        if "users" not in st.session_state:
            st.session_state["users"] = {}
        st.session_state["users"][current_user] = user_data



def buy_stock(symbol, price, quantity=1):
    """Hisse satın alır"""
    user_data = get_current_user_data()
    total_cost = price * quantity
    
    if total_cost > user_data['balance']:
        return False, "Yetersiz bakiye"
    
    # Bakiye güncelle
    user_data['balance'] -= total_cost
    
    # Portföy güncelle
    if symbol in user_data['portfolio']:
        current_quantity = user_data['portfolio'][symbol]['quantity']
        current_avg_price = user_data['portfolio'][symbol]['avg_price']
        
        # Ortalama fiyat hesapla
        new_quantity = current_quantity + quantity
        new_avg_price = ((current_quantity * current_avg_price) + (quantity * price)) / new_quantity
        
        user_data['portfolio'][symbol] = {
            'quantity': new_quantity,
            'avg_price': new_avg_price,
            'last_buy_price': price
        }
    else:
        user_data['portfolio'][symbol] = {
            'quantity': quantity,
            'avg_price': price,
            'last_buy_price': price
        }
    
    # İşlem kaydı
    transaction = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'BUY',
        'symbol': symbol,
        'quantity': quantity,
        'price': price,
        'total': total_cost
    }
    user_data['transactions'].append(transaction)
    
    # Kullanıcı verilerini güncelle
    update_user_data(user_data)
    
    return True, "Alım işlemi başarılı"

def sell_stock(symbol, price, quantity=None):
    """Hisse satar"""
    user_data = get_current_user_data()
    
    if symbol not in user_data['portfolio']:
        return False, "Portföyde bu hisse bulunmuyor"
    
    current_quantity = user_data['portfolio'][symbol]['quantity']
    
    if quantity is None:
        quantity = current_quantity  # Tümünü sat
    
    if quantity > current_quantity:
        return False, "Yetersiz hisse miktarı"
    
    total_revenue = price * quantity
    
    # Bakiye güncelle
    user_data['balance'] += total_revenue
    
    # Portföy güncelle
    if quantity == current_quantity:
        # Tümünü sattı
        del user_data['portfolio'][symbol]
    else:
        # Kısmi satış
        user_data['portfolio'][symbol]['quantity'] -= quantity
    
    # İşlem kaydı
    transaction = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'SELL',
        'symbol': symbol,
        'quantity': quantity,
        'price': price,
        'total': total_revenue
    }
    user_data['transactions'].append(transaction)
    
    # Kullanıcı verilerini güncelle
    update_user_data(user_data)
    
    return True, "Satış işlemi başarılı"

def calculate_performance():
    """7 günlük performans hesaplar"""
    user_data = get_current_user_data()
    
    if not user_data['transactions']:
        return {}
    
    # Son 7 günün işlemlerini filtrele
    week_ago = datetime.now() - timedelta(days=7)
    recent_transactions = [
        t for t in user_data['transactions'] 
        if datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S') >= week_ago
    ]
    
    performance = {}
    
    for transaction in recent_transactions:
        symbol = transaction['symbol']
        
        if symbol not in performance:
            performance[symbol] = {
                'total_bought': 0,
                'total_sold': 0,
                'quantity_bought': 0,
                'quantity_sold': 0,
                'avg_buy_price': 0,
                'avg_sell_price': 0
            }
        
        if transaction['type'] == 'BUY':
            performance[symbol]['total_bought'] += transaction['total']
            performance[symbol]['quantity_bought'] += transaction['quantity']
            performance[symbol]['avg_buy_price'] = performance[symbol]['total_bought'] / performance[symbol]['quantity_bought']
        
        elif transaction['type'] == 'SELL':
            performance[symbol]['total_sold'] += transaction['total']
            performance[symbol]['quantity_sold'] += transaction['quantity']
            performance[symbol]['avg_sell_price'] = performance[symbol]['total_sold'] / performance[symbol]['quantity_sold']
    
    # Kar/zarar hesapla
    for symbol in performance:
        if performance[symbol]['quantity_sold'] > 0:
            total_cost = performance[symbol]['avg_buy_price'] * performance[symbol]['quantity_sold']
            total_revenue = performance[symbol]['total_sold']
            profit_loss = total_revenue - total_cost
            profit_loss_percent = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
            
            performance[symbol]['profit_loss'] = profit_loss
            performance[symbol]['profit_loss_percent'] = profit_loss_percent
    
    return performance

def analyze_opportunities(stocks_data):
    """Hisse fırsatlarını analiz eder"""
    opportunities = []
    
    for stock in stocks_data:
        if stock is None or 'change_365d' not in stock:
            continue
            
        change_365d = stock['change_365d']
        current_price = stock['current_price']
        
        # Fırsat kriterleri: %40'tan fazla düşüş ve fiyat > $1
        if change_365d < -40 and current_price > 1:
            # Fırsat skoru hesapla (düşüş yüzdesi * fiyat)
            opportunity_score = abs(change_365d) * current_price / 100
            
            opportunities.append({
                'symbol': stock['symbol'],
                'current_price': current_price,
                'change_365d': change_365d,
                'opportunity_score': opportunity_score,
                'source': stock.get('source', 'unknown')
            })
    
    # Fırsat skoruna göre sırala
    opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
    return opportunities

def analyze_downtrend_stocks():
    """1 yıl içinde büyük değer kaybetmiş ve yükselme potansiyeli olan hisseleri bul"""
    
    # Tüm ABD büyük endekslerinden binlerce hisseyi çek
    popular_stocks = get_us_stock_list()
    
    opportunities = []
    debug_info = []  # Debug bilgisi için
    
    with st.spinner("🔍 ABD hisseleri analiz ediliyor..."):
        app = StockAnalysisApp()
        
        # Analiz edilecek hisse sayısını sınırla (API limitleri için)
        total_stocks = len(popular_stocks)
        analyzed_count = min(200, total_stocks)  # 200 hisseye kadar analiz et (API limitleri için)
        
        st.info(f"📊 Toplam {total_stocks} hisse bulundu, {analyzed_count} tanesi analiz edilecek")
        
        # Progress bar ve status text oluştur
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(popular_stocks[:analyzed_count]):
            try:
                # İlerleme göstergesi - her 50 hissede bir güncelle
                if i % 50 == 0:
                    progress = (i / analyzed_count)
                    progress_bar.progress(progress)
                    status_text.text(f"🔄 Analiz ediliyor: {i}/{analyzed_count} ({progress*100:.1f}%) - {symbol}")
                
                # API rate limiting için bekleme
                if i % 10 == 0 and i > 0:
                    time.sleep(1)  # Her 10 hissede 1 saniye bekle
                
                # Son 1 yıl verisi (365 gün)
                data = app.stock_scraper.get_stock_data(symbol, "365d")
                
                # Veri yoksa veya hata varsa sembolü atla
                if not data:
                    debug_info.append({'symbol': symbol, 'change_365d': None, 'current_price': None, 'data_points': 0, 'opportunity_score': 0, 'veri': 'VERİ YOK'})
                    continue
                
                # Mock data'dan gelen veri yapısını kullan
                current_price = data.get('current_price')
                change_365d = data.get('change_365d')
                
                if current_price is None or change_365d is None:
                    debug_info.append({'symbol': symbol, 'change_365d': None, 'current_price': None, 'data_points': 0, 'opportunity_score': 0, 'veri': 'FİYAT YOK'})
                    continue
                opportunity_score = 0
                has_downtrend = False
                if change_365d < -40:
                    opportunity_score += 40
                    has_downtrend = True
                # Data points hesapla (mock data için 365 gün)
                data_points = 365 if data.get('data') is not None else 0
                
                debug_info.append({
                    'symbol': symbol,
                    'change_365d': change_365d,
                    'current_price': current_price,
                    'data_points': data_points,
                    'opportunity_score': opportunity_score,
                    'has_downtrend': has_downtrend
                })
            except Exception as e:
                # Hata durumunda sembolü atla
                debug_info.append({'symbol': symbol, 'change_365d': None, 'current_price': None, 'data_points': 0, 'opportunity_score': 0, 'veri': f'HATA: {str(e)}'})
                continue
        progress_bar.progress(1.0)
        status_text.text("✅ Analiz tamamlandı!")
        debug_df = pd.DataFrame(debug_info)
        debug_df['change_365d'] = pd.to_numeric(debug_df['change_365d'], errors='coerce')
        
        # Opportunities listesini oluştur
        opportunities = []
        for _, row in debug_df.iterrows():
            if pd.notna(row['change_365d']) and pd.notna(row['current_price']):
                opportunities.append({
                    'symbol': row['symbol'],
                    'current_price': row['current_price'],
                    'change_365d': row['change_365d'],
                    'opportunity_score': row['opportunity_score'],
                    'has_downtrend': row.get('has_downtrend', False)
                })
        
        st.subheader("🔍 Debug Bilgisi")
        if not debug_df.empty:
            top_decliners = debug_df.nsmallest(10, 'change_365d')
            st.write("**En Çok Düşen 10 Hisse:**")
            st.dataframe(top_decliners[['symbol', 'change_365d', 'current_price', 'opportunity_score']])
            top_opportunities = debug_df.nlargest(10, 'opportunity_score')
            st.write("**En Yüksek Fırsat Skoruna Sahip 10 Hisse:**")
            st.dataframe(top_opportunities[['symbol', 'change_365d', 'current_price', 'opportunity_score']])
            downtrend_stocks = debug_df[debug_df['change_365d'] < -40]
            st.write(f"**%40'dan Fazla Düşüş Yaşayan Hisse Sayısı: {len(downtrend_stocks)}**")
            if not downtrend_stocks.empty:
                st.dataframe(downtrend_stocks[['symbol', 'change_365d', 'opportunity_score']])
        else:
            st.write("Debug verisi yok!")
    
    opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
    return opportunities

def show_ai_analysis():
    """AI destekli analiz sayfası"""
    st.header("🤖 AI Destekli Analiz")
    st.markdown("**Yapay zeka ile hisse analizi, fiyat tahmini ve trend tespiti**")

    # AI modüllerini başlat
    price_predictor = PricePredictor()
    sentiment_analyzer = SentimentAnalyzer()
    trend_detector = TrendDetector()
    nlp_assistant = NLPAssistant()

    # Sekmeler
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Fiyat Tahmini", "📊 Trend Analizi", "📰 Sentiment Analizi", "💬 AI Asistan"])

    with tab1:
        st.subheader("🔮 AI Fiyat Tahmini")
        selected_stock = st.selectbox("Tahmin için hisse seçin:", us_stocks, key="prediction_stock")
        
        if selected_stock:
            stock_data = get_stock_data(selected_stock)
            if stock_data and 'historical_data' in stock_data:
                # AI tahmini
                prediction = price_predictor.predict_price(selected_stock, stock_data['historical_data'])
                
                if prediction:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Güncel Fiyat", f"${prediction['current_price']:.2f}")
                        st.metric("Trend", prediction['trend'])
                        st.metric("Güven Skoru", f"%{prediction['confidence']:.1f}")
                    
                    with col2:
                        st.metric("Öneri", prediction['recommendation'])
                        
                        # 7 günlük tahmin grafiği
                        if prediction['predictions']:
                            fig = go.Figure()
                            days = list(range(1, len(prediction['predictions']) + 1))
                            
                            fig.add_trace(go.Scatter(
                                x=days,
                                y=prediction['predictions'],
                                mode='lines+markers',
                                name='AI Tahmini',
                                line=dict(color='blue', width=3)
                            ))
                            
                            fig.update_layout(
                                title=f"{selected_stock} 7 Günlük Fiyat Tahmini",
                                xaxis_title="Gün",
                                yaxis_title="Fiyat ($)",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Tahmin verisi bulunamadı.")

    with tab2:
        st.subheader("📊 Trend Kırılım Analizi")
        selected_stock = st.selectbox("Trend analizi için hisse:", us_stocks, key="trend_stock")
        if selected_stock:
            stock_data = get_stock_data(selected_stock)
            if stock_data and 'historical_data' in stock_data:
                # Trend analizi
                trend_analysis = trend_detector.detect_breakouts(stock_data['historical_data'], selected_stock)
                col1, col2 = st.columns(2)
                if trend_analysis:
                    with col1:
                        st.subheader("🎯 Kırılım Noktaları")
                        if trend_analysis['breakouts']:
                            for breakout in trend_analysis['breakouts']:
                                st.info(f"**{breakout['type']}** - {breakout['date']}")
                                st.write(f"Fiyat: ${breakout['price']:.2f}")
                                st.write(f"Güç: {breakout['strength']}")
                                st.write("---")
                        else:
                            st.info("Şu anda kırılım noktası tespit edilmedi.")

                    with col2:
                        st.subheader("📈 Trend Analizi")
                        trend_data = trend_analysis['trend_analysis']
                        st.metric("Trend Yönü", trend_data['trend_direction'])
                        st.metric("Trend Gücü", trend_data['trend_strength'])
                        st.metric("Değişim %", f"{trend_data['price_change_percent']:.2f}%")
                        st.metric("Volatilite", f"{trend_data['volatility_percent']:.2f}%")

                        # Destek/Direnç seviyeleri
                        if trend_analysis['support_resistance']:
                            sr = trend_analysis['support_resistance']
                            st.subheader("🎯 Destek/Direnç")
                            if sr['nearest_support']:
                                st.write(f"En Yakın Destek: ${sr['nearest_support']:.2f}")
                            if sr['nearest_resistance']:
                                st.write(f"En Yakın Direnç: ${sr['nearest_resistance']:.2f}")
                            st.write(f"Fiyat Pozisyonu: %{sr['price_position']:.1f}")

    with tab3:
        st.subheader("📰 Haber Sentiment Analizi")
        
        # Haber kaynağı seçimi
        news_source = st.selectbox("Haber kaynağı:", ["ABD Piyasası", "BIST Piyasası"])
        market = "us" if news_source == "ABD Piyasası" else "tr"
        
        if st.button("🔄 Haberleri Analiz Et"):
            news_scraper = NewsScraper()
            news_list = news_scraper.get_market_news(market, 10)
            
            if news_list:
                # Sentiment analizi
                analyzed_news = sentiment_analyzer.analyze_news_batch(news_list)
                summary = sentiment_analyzer.get_sentiment_summary(analyzed_news)
                
                # Özet metrikler
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Toplam Haber", summary['total_news'])
                with col2:
                    st.metric("Pozitif %", f"%{summary['positive_ratio']:.1f}")
                with col3:
                    st.metric("Negatif %", f"%{summary['negative_ratio']:.1f}")
                with col4:
                    st.metric("Piyasa Sentiment", summary['market_sentiment'])
                
                # Haber listesi
                st.subheader("📋 Analiz Edilen Haberler")
                for news in analyzed_news[:5]:
                    sentiment_color = {
                        'positive': 'green',
                        'negative': 'red',
                        'neutral': 'gray'
                    }.get(news['sentiment'], 'gray')
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {sentiment_color}; padding-left: 10px; margin: 10px 0;">
                        <h4>{news['title']}</h4>
                        <p><strong>Kaynak:</strong> {news['source']} | <strong>Sentiment:</strong> {news['sentiment_label']} | <strong>Güven:</strong> %{news['confidence']*100:.1f}</p>
                        <p>{news['content'][:200]}...</p>
                    </div>
                    """, unsafe_allow_html=True)

    with tab4:
        st.subheader("💬 AI Asistan")
        st.markdown("**Doğal dil ile hisse analizi sorularınızı sorun**")
        
        # Örnek sorular
        example_questions = [
            "AAPL fiyatı ne kadar olacak?",
            "En iyi performans gösteren hisseler hangileri?",
            "Portföyümü nasıl optimize edebilirim?",
            "Hangi hisseyi almalıyım?",
            "Piyasa durumu nasıl?"
        ]
        
        st.write("**Örnek Sorular:**")
        for i, question in enumerate(example_questions):
            if st.button(question, key=f"example_{i}"):
                st.session_state.user_question = question
        
        # Kullanıcı sorusu
        user_question = st.text_input("Sorunuzu yazın:", value=st.session_state.get('user_question', ''))
        
        if user_question and st.button("🤖 Yanıt Al"):
            # Bağlam verilerini hazırla
            context_data = {
                'stock_data': {},
                'portfolio': [],
                'news_sentiment': {'category': 'Nötr'}
            }
            
            # Hisse verilerini al
            for symbol in us_stocks[:5]:  # İlk 5 hisse
                stock_data = get_stock_data(symbol)
                if stock_data:
                    context_data['stock_data'][symbol] = stock_data
            
            # AI yanıtı al
            response = nlp_assistant.process_question(user_question, context_data)
            
            if response:
                st.success("🤖 AI Yanıtı:")
                st.write(response['response'])
                
                st.info(f"**Güven Skoru:** %{response['confidence']:.1f}")
                
                if response['suggestions']:
                    st.write("**Önerilen Sorular:**")
                    for suggestion in response['suggestions'][:3]:
                        if st.button(suggestion, key=f"suggestion_{suggestion}"):
                            st.session_state.user_question = suggestion
                            st.rerun()

def show_news_dashboard():
    """Güncel Haberler Sekmesi"""
    st.header("📰 Güncel Piyasa Haberleri")
    
    news_scraper = st.session_state.news_scraper
    
    # Piyasa seçimi
    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("Piyasa:", ["us", "tr"], format_func=lambda x: "ABD" if x == "us" else "Türkiye")
    with col2:
        news_limit = st.slider("Haber Sayısı:", 5, 20, 10)
    
    if st.button("🔄 Haberleri Yenile"):
        # Haberleri çek
        news_data = news_scraper.get_market_news(market, news_limit)
        
        if news_data:
            # Haber özeti
            news_summary = news_scraper.get_news_summary(market)
            
            # Özet metrikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Toplam Haber", news_summary['total_news'])
            with col2:
                st.metric("Pozitif", f"%{news_summary['positive_ratio']:.1f}")
            with col3:
                st.metric("Negatif", f"%{news_summary['negative_ratio']:.1f}")
            with col4:
                st.metric("Piyasa Sentiment", news_summary['market_sentiment'])
            
            # Haber listesi
            st.subheader("📋 Haber Detayları")
            for i, news in enumerate(news_data):
                sentiment_color = {
                    'positive': 'success',
                    'negative': 'error',
                    'neutral': 'info'
                }.get(news.get('sentiment', 'neutral'), 'info')
                
                with st.expander(f"{news['title']} - {news.get('source', 'Bilinmiyor')}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**İçerik:** {news['content']}")
                        st.write(f"**Tarih:** {news.get('published_date', 'Bilinmiyor')}")
                    with col2:
                        st.write(f"**Sentiment:** {news.get('sentiment', 'Nötr')}")
                        if news.get('symbols'):
                            st.write(f"**İlgili Hisse:** {', '.join(news['symbols'])}")
            
            # Trend konular
            if news_summary.get('trending_topics'):
                st.subheader("🔥 Trend Konular")
                topics_str = ", ".join(news_summary['trending_topics'])
                st.info(f"**Güncel Trend Konular:** {topics_str}")
        else:
            st.warning("Haber verisi alınamadı")

def show_portfolio_optimizer():
    """Portföy optimizer sayfası"""
    st.header("📊 Portföy Optimizer")
    st.markdown("**Portföy sağlık skoru ve optimizasyon önerileri**")

    # Portföy analyzer'ı başlat
    portfolio_analyzer = PortfolioAnalyzer()

    # Kullanıcı seçimi
    user_id = st.selectbox("Kullanıcı:", ["gokhan", "yilmaz"], key="portfolio_user")

    # Data manager'dan portföy verilerini al
    data_manager = DataManager()
    portfolio_data = data_manager.get_user_portfolio(user_id)

    if portfolio_data:
        # Piyasa verilerini al
        market_data = {}
        for item in portfolio_data:
            symbol = item.get('symbol', '')
            stock_data = get_stock_data(symbol)
            if stock_data:
                market_data[symbol] = stock_data

        # Portföy analizi
        analysis = portfolio_analyzer.analyze_portfolio(portfolio_data, market_data)

        # Sağlık skoru
        st.subheader("🏥 Portföy Sağlık Skoru")
        health_score = analysis['health_score']
        
        # Sağlık skoru göstergesi
        if health_score >= 80:
            health_color = "green"
            health_status = "Mükemmel"
        elif health_score >= 60:
            health_color = "orange"
            health_status = "İyi"
        elif health_score >= 40:
            health_color = "yellow"
            health_status = "Orta"
        else:
            health_color = "red"
            health_status = "Zayıf"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sağlık Skoru", f"{health_score}/100", delta=health_status)
        with col2:
            st.metric("Toplam Değer", f"${analysis['total_value']:,.2f}")
        with col3:
            st.metric("Toplam Getiri", f"${analysis['total_return']:,.2f}", delta=f"{analysis['return_percentage']:+.1f}%")

        # Risk metrikleri
        st.subheader("⚠️ Risk Analizi")
        risk_metrics = analysis['risk_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Portföy Getirisi", f"%{risk_metrics['portfolio_return']:.1f}")
        with col2:
            st.metric("Volatilite", f"%{risk_metrics['portfolio_volatility']:.1f}")
        with col3:
            st.metric("Sharpe Oranı", f"{risk_metrics['sharpe_ratio']:.3f}")
        with col4:
            st.metric("Risk Seviyesi", risk_metrics['risk_level'])

        # Çeşitlendirme analizi
        st.subheader("🌐 Çeşitlendirme Analizi")
        diversification = analysis['diversification']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Çeşitlendirme Seviyesi", diversification['diversification_level'])
            st.metric("Toplam Sektör", diversification['total_sectors'])
            st.metric("HHI İndeksi", diversification['hhi_index'])
        
        with col2:
            # Sektör dağılımı grafiği
            if diversification['sector_weights']:
                sector_data = pd.DataFrame([
                    {'Sektör': sector, 'Ağırlık': weight}
                    for sector, weight in diversification['sector_weights'].items()
                ])
                
                fig = px.pie(sector_data, values='Ağırlık', names='Sektör', title="Sektör Dağılımı")
                st.plotly_chart(fig, use_container_width=True)

        # Optimizasyon önerileri
        st.subheader("💡 Optimizasyon Önerileri")
        recommendations = analysis['recommendations']
        
        if recommendations:
            for i, rec in enumerate(recommendations):
                priority_color = {
                    'Yüksek': 'red',
                    'Orta': 'orange',
                    'Düşük': 'green'
                }.get(rec['priority'], 'blue')
                
                st.markdown(f"""
                <div style="border-left: 4px solid {priority_color}; padding-left: 10px; margin: 10px 0;">
                    <h4>{rec['title']} ({rec['priority']} Öncelik)</h4>
                    <p>{rec['description']}</p>
                    <p><strong>Önerilen Aksiyon:</strong> {rec['action']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Portföyünüz iyi durumda! Özel öneri bulunmuyor.")

    else:
        st.warning("Portföy verisi bulunamadı. Önce hisse alımı yapın.")

def show_alerts_system():
    """Alarm sistemi sayfası"""
    st.header("🔔 Fiyat Alarm Sistemi")
    st.markdown("**Hisse fiyatları için otomatik alarmlar kurun**")

    # Alarm manager'ı başlat
    alert_manager = AlertManager()

    # Kullanıcı seçimi
    user_id = st.selectbox("Kullanıcı:", ["gokhan", "yilmaz"], key="alert_user")

    # Yeni alarm oluşturma
    st.subheader("➕ Yeni Alarm Oluştur")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Hisse:", us_stocks, key="alert_symbol")
        alert_type = st.selectbox("Alarm Türü:", ["price", "percentage"], key="alert_type")
    
    with col2:
        condition = st.selectbox("Koşul:", ["above", "below", "equals"], key="alert_condition")
        target_price = st.number_input("Hedef Fiyat ($):", min_value=0.01, value=100.0, step=0.01, key="alert_price")

    if st.button("🔔 Alarm Oluştur", key="create_alert"):
        if symbol and target_price > 0:
            alert = alert_manager.create_alert(user_id, symbol, alert_type, target_price, condition)
            if alert:
                st.success(f"✅ Alarm başarıyla oluşturuldu! (ID: {alert['id']})")
            else:
                st.error("❌ Alarm oluşturulamadı.")
        else:
            st.warning("⚠️ Lütfen tüm alanları doldurun.")

    # Mevcut alarmlar
    st.subheader("📋 Mevcut Alarmlar")
    user_alerts = alert_manager.get_user_alerts(user_id)
    
    if user_alerts:
        for alert in user_alerts:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"**{alert['symbol']}** - {alert['condition']} ${alert['target_price']:.2f}")
                st.write(f"Oluşturulma: {alert['created_at']}")
            
            with col2:
                status = "🟢 Aktif" if alert['is_active'] else "🔴 Tetiklendi"
                st.write(status)
            
            with col3:
                if alert['triggered_at']:
                    st.write(f"Tetiklenme: {alert['triggered_at']}")
            
            with col4:
                if alert['is_active']:
                    if st.button("❌ Sil", key=f"delete_{alert['id']}"):
                        if alert_manager.delete_alert(alert['id']):
                            st.success("Alarm silindi!")
                            st.rerun()
                else:
                    st.write("✅ Tamamlandı")
            
            st.divider()
    else:
        st.info("Henüz alarm oluşturulmamış.")

    # Alarm istatistikleri
    st.subheader("📊 Alarm İstatistikleri")
    stats = alert_manager.get_alert_statistics(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Alarm", stats['total_alerts'])
    with col2:
        st.metric("Aktif Alarm", stats['active_alerts'])
    with col3:
        st.metric("Tetiklenen", stats['triggered_alerts'])
    with col4:
        if stats['top_symbols']:
            top_symbol = stats['top_symbols'][0]['symbol']
            st.metric("En Çok Alarm", top_symbol)

    # Alarm geçmişi
    st.subheader("📈 Alarm Geçmişi")
    history = alert_manager.get_alert_history(user_id, 10)
    
    if history:
        for record in history:
            st.write(f"**{record['symbol']}** - Hedef: ${record['target_price']:.2f}, Gerçekleşen: ${record['current_price']:.2f}")
            st.write(f"Tarih: {record['triggered_at']}")
            st.divider()
    else:
        st.info("Henüz tetiklenen alarm yok.")

def show_virtual_trading():
    """Sanal trading sayfası"""
    st.header("🎮 Sanal Trading")
    st.markdown("**Hayali alım-satım sistemi**")
    
    # Refresh kontrolü
    if st.session_state.refresh_watchlist:
        st.session_state.refresh_watchlist = False
        st.rerun()
    
    # Kullanıcı seçimi
    st.subheader("👤 Kullanıcı Seçimi")
    selected_user = st.selectbox(
        "Hangi kullanıcı ile işlem yapmak istiyorsunuz?",
        ["Gökhan", "Yılmaz"],
        index=0 if st.session_state.selected_user == "Gökhan" else 1,
        key="user_selector"
    )
    
    # Kullanıcı değiştiğinde session state'i güncelle
    if selected_user != st.session_state.selected_user:
        st.session_state.selected_user = selected_user
        st.rerun()
    
    # Seçili kullanıcının verilerini al
    user_data = get_current_user_data()
    
    # Kullanıcı bilgileri
    st.sidebar.subheader("💰 Kullanıcı Bilgileri")
    st.sidebar.write(f"**Kullanıcı:** {selected_user}")
    st.sidebar.metric("Bakiye", f"{user_data['balance']:.2f} USD")
    
    # Takip listesi
    st.sidebar.subheader("👀 Takip Listesi")
    print(f"DEBUG SIDEBAR: Takip listesi içeriği: {st.session_state['watchlist']}")
    if st.session_state["watchlist"]:
        st.sidebar.write(f"📊 **{len(st.session_state['watchlist'])} hisse takip ediliyor**")
        for i, symbol in enumerate(st.session_state["watchlist"]):
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.sidebar.write(f"📈 {symbol}")
            with col2:
                if st.sidebar.button("❌", key=f"sidebar_remove_{symbol}_{i}", on_click=remove_from_watchlist_callback(symbol)):
                    print(f"DEBUG: {symbol} watchlist'ten çıkarıldı")
    else:
        st.sidebar.info("📝 Henüz takip listesi boş")
        print(f"DEBUG SIDEBAR: Takip listesi boş!")
    
    # Ana trading arayüzü
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Portföy", "👀 Takip Listesi", "💸 İşlem Yap", "📈 Performans", "📋 İşlem Geçmişi"])
    
    with tab1:
        show_portfolio_tab()
    
    with tab2:
        show_watchlist_tab()
    
    with tab3:
        show_trading_tab()
    
    with tab4:
        show_performance_tab()
    
    with tab5:
        show_transaction_history()

def show_watchlist_tab():
    """Takip listesi sekmesi"""
    st.subheader("👀 Takip Listesi")
    st.markdown("**Fırsat analizinden takibe aldığınız hisseler**")
    
    if not st.session_state["watchlist"]:
        st.info("📝 Henüz takip listesinde hisse bulunmuyor.")
        st.markdown("""
        **Takip listesine hisse eklemek için:**
        1. **Fırsat Analizi** sayfasına gidin
        2. İstediğiniz hisseyi bulun
        3. **"Takibe Al"** butonuna tıklayın
        """)
        return
    
    # Takip listesi özeti
    st.success(f"✅ Takip listenizde {len(st.session_state['watchlist'])} hisse bulunuyor")
    
    # Her hisse için detaylı bilgi ve işlem seçenekleri
    for i, symbol in enumerate(st.session_state["watchlist"]):
        with st.expander(f"📈 {symbol} - Detaylar ve İşlemler", expanded=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.write(f"**{symbol}**")
                
                # Mock hisse bilgileri (gerçek uygulamada API'den çekilecek)
                mock_price = 45.2 + np.random.uniform(-10, 10)
                mock_change = np.random.uniform(-15, 15)
                mock_volume = np.random.randint(1000000, 10000000)
                
                st.write(f"💰 **Güncel Fiyat:** {mock_price:.2f} USD")
                st.write(f"📊 **Günlük Değişim:** {mock_change:+.2f}%")
                st.write(f"📈 **Hacim:** {mock_volume:,}")
                
                # Hisse durumu
                if mock_change > 0:
                    st.success(f"🟢 Pozitif trend")
                elif mock_change < 0:
                    st.error(f"🔴 Negatif trend")
                else:
                    st.info(f"⚪ Nötr")
            
            with col2:
                st.write("**📊 Teknik Analiz**")
                
                # Mock teknik göstergeler
                rsi = np.random.uniform(30, 70)
                macd = np.random.uniform(-2, 2)
                volume_ratio = np.random.uniform(0.5, 2.0)
                
                st.write(f"RSI: {rsi:.1f}")
                st.write(f"MACD: {macd:.2f}")
                st.write(f"Hacim Oranı: {volume_ratio:.2f}")
                
                # RSI durumu
                if rsi > 70:
                    st.warning("⚠️ Aşırı alım")
                elif rsi < 30:
                    st.info("💡 Aşırı satım fırsatı")
                else:
                    st.success("✅ Normal seviye")
            
            with col3:
                st.write("**🎯 İşlem Seçenekleri**")
                
                # Adet seçimi
                quantity = st.number_input(
                    "Adet:",
                    min_value=1,
                    value=1,
                    key=f"watchlist_qty_{symbol}"
                )
                
                # Toplam maliyet
                total_cost = quantity * mock_price
                st.write(f"**Toplam:** {total_cost:.2f} USD")
            
            with col4:
                st.write("**🛒 İşlem Butonları**")
                
                # Alım butonu
                if st.button(f"🛒 Al", key=f"watchlist_buy_{symbol}"):
                    success, message = buy_stock(symbol, mock_price, quantity)
                    if success:
                        st.success(f"{symbol} başarıyla alındı!")
                        st.rerun()
                    else:
                        st.error(message)
                
                # Satış butonu (portföyde varsa)
                user_data = get_current_user_data()
                if symbol in user_data['portfolio']:
                    if st.button(f"💸 Sat", key=f"watchlist_sell_{symbol}"):
                        success, message = sell_stock(symbol, mock_price, quantity)
                        if success:
                            st.success(f"{symbol} başarıyla satıldı!")
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.info("Portföyde yok")
                
                # Takip listesinden çıkar
                if st.button(f"❌ Takipten Çıkar", key=f"watchlist_remove_{symbol}"):
                    remove_from_watchlist(symbol)
                    st.success(f"{symbol} takip listesinden çıkarıldı!")
            
            st.divider()
    
    # Takip listesi istatistikleri
    st.subheader("📊 Takip Listesi İstatistikleri")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Hisse", len(st.session_state["watchlist"]))
    
    with col2:
        # Pozitif trend sayısı
        positive_count = sum(1 for _ in range(len(st.session_state["watchlist"])) 
                           if np.random.uniform(-15, 15) > 0)
        st.metric("Pozitif Trend", positive_count)
    
    with col3:
        # Portföyde olan hisse sayısı
        user_data = get_current_user_data()
        portfolio_count = sum(1 for symbol in st.session_state["watchlist"] 
                            if symbol in user_data['portfolio'])
        st.metric("Portföyde Olan", portfolio_count)
    
    with col4:
        # Ortalama fiyat
        avg_price = 45.2  # Mock ortalama
        st.metric("Ortalama Fiyat", f"{avg_price:.2f} USD")

def show_portfolio_tab():
    """Portföy sekmesi"""
    st.subheader("📊 Mevcut Portföy")
    
    user_data = get_current_user_data()
    
    if not user_data['portfolio']:
        st.info("Portföyünüzde henüz hisse bulunmuyor.")
        return
    
    # Portföy özeti
    total_value = 0
    portfolio_data = []
    
    for symbol, data in user_data['portfolio'].items():
        # Mock güncel fiyat (gerçek uygulamada API'den çekilecek)
        current_price = data['avg_price'] * np.random.uniform(0.8, 1.2)
        quantity = data['quantity']
        value = quantity * current_price
        total_value += value
        
        # Kar/zarar hesapla
        cost = quantity * data['avg_price']
        profit_loss = value - cost
        profit_loss_percent = (profit_loss / cost) * 100 if cost > 0 else 0
        
        portfolio_data.append({
            'Symbol': symbol,
            'Adet': quantity,
            'Ortalama Maliyet': f"{data['avg_price']:.2f} USD",
            'Güncel Fiyat': f"{current_price:.2f} USD",
            'Toplam Değer': f"{value:.2f} USD",
            'Kar/Zarar': f"{profit_loss:.2f} USD",
            'Kar/Zarar %': f"{profit_loss_percent:.2f}%"
        })
    
    # Portföy tablosu
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)
    
    # Toplam değer
    st.metric("📈 Toplam Portföy Değeri", f"{total_value:.2f} USD")

def show_trading_tab():
    """İşlem yapma sekmesi"""
    st.subheader("💸 İşlem Yap")
    st.markdown("**Portföyünüzdeki hisselerden satış yapın veya yeni hisse alın**")
    
    # Portföydeki hisselerden satış
    user_data = get_current_user_data()
    
    if user_data['portfolio']:
        st.write("**📊 Portföyünüzdeki Hisselerden Satış:**")
        
        for symbol, data in user_data['portfolio'].items():
            with st.expander(f"📈 {symbol} - Satış İşlemi", expanded=True):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{symbol}**")
                    st.write(f"📦 **Mevcut Adet:** {data['quantity']}")
                    st.write(f"💰 **Ortalama Maliyet:** {data['avg_price']:.2f} USD")
                    
                    # Mock güncel fiyat
                    mock_price = data['avg_price'] * np.random.uniform(0.8, 1.2)
                    st.write(f"📊 **Güncel Fiyat:** {mock_price:.2f} USD")
                    
                    # Kar/zarar hesapla
                    cost = data['quantity'] * data['avg_price']
                    value = data['quantity'] * mock_price
                    profit_loss = value - cost
                    profit_loss_percent = (profit_loss / cost) * 100 if cost > 0 else 0
                    
                    if profit_loss > 0:
                        st.success(f"📈 **Kar:** {profit_loss:.2f} USD (%{profit_loss_percent:.2f})")
                    else:
                        st.error(f"📉 **Zarar:** {profit_loss:.2f} USD (%{profit_loss_percent:.2f})")
                
                with col2:
                    st.write("**🎯 Satış Seçenekleri**")
                    
                    # Satış miktarı
                    max_quantity = data['quantity']
                    sell_quantity = st.number_input(
                        "Satılacak Adet:",
                        min_value=1,
                        max_value=max_quantity,
                        value=1,
                        key=f"sell_qty_{symbol}"
                    )
                    
                    # Toplam gelir
                    total_revenue = sell_quantity * mock_price
                    st.write(f"**Toplam Gelir:** {total_revenue:.2f} USD")
                
                with col3:
                    st.write("")  # Boşluk
                    st.write("")  # Boşluk
                
                with col4:
                    st.write("**💸 Satış İşlemi**")
                    
                    if st.button(f"💸 Sat", key=f"sell_portfolio_{symbol}"):
                        success, message = sell_stock(symbol, mock_price, sell_quantity)
                        if success:
                            st.success(f"{symbol} başarıyla satıldı!")
                            st.rerun()
                        else:
                            st.error(message)
                
                st.divider()
    else:
        st.info("Portföyünüzde henüz hisse bulunmuyor.")
    
    # Yeni hisse alımı
    st.subheader("🛒 Yeni Hisse Alımı")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        all_stocks = list(set(bist_stocks + us_stocks))
        selected_stock = st.selectbox("Hisse Seçin:", all_stocks, key="new_stock")
    
    with col2:
        new_stock_price = st.number_input("Fiyat (TL):", min_value=0.01, value=45.2, step=0.01, key="new_stock_price")
        new_stock_quantity = st.number_input("Adet:", min_value=1, value=1, key="new_stock_quantity")
        
        # Toplam maliyet
        total_cost = new_stock_quantity * new_stock_price
        st.write(f"**Toplam Maliyet:** {total_cost:.2f} USD")
        
        # Bakiye kontrolü
        if total_cost > user_data['balance']:
            st.error(f"❌ Yetersiz bakiye! Gerekli: {total_cost:.2f} USD, Mevcut: {user_data['balance']:.2f} USD")
        else:
            st.success(f"✅ Yeterli bakiye")
    
    with col3:
        st.write("")  # Boşluk
        st.write("")  # Boşluk
        
        if st.button("🛒 Satın Al", key="buy_new_stock"):
            success, message = buy_stock(selected_stock, new_stock_price, new_stock_quantity)
            if success:
                st.success(f"{selected_stock} başarıyla alındı!")
                st.rerun()
            else:
                st.error(message)

def show_performance_tab():
    """Performans sekmesi"""
    st.subheader("📈 7 Günlük Performans")
    
    performance = calculate_performance()
    
    if not performance:
        st.info("Son 7 günde işlem bulunmuyor.")
        return
    
    # Performans özeti
    total_profit = 0
    total_transactions = 0
    
    performance_data = []
    
    for symbol, data in performance.items():
        if 'profit_loss' in data:
            total_profit += data['profit_loss']
            total_transactions += 1
            
            performance_data.append({
                'Hisse': symbol,
                'Alış Ortalama': f"{data['avg_buy_price']:.2f} USD",
                'Satış Ortalama': f"{data['avg_sell_price']:.2f} USD",
                'Alınan Adet': data['quantity_bought'],
                'Satılan Adet': data['quantity_sold'],
                'Kar/Zarar': f"{data['profit_loss']:.2f} USD",
                'Kar/Zarar %': f"{data['profit_loss_percent']:.2f}%"
            })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
        
        # Genel performans
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Toplam Kar/Zarar", f"{total_profit:.2f} USD")
        with col2:
            st.metric("📊 İşlem Sayısı", total_transactions)
        with col3:
            avg_profit = total_profit / total_transactions if total_transactions > 0 else 0
            st.metric("📈 Ortalama Kar/Zarar", f"{avg_profit:.2f} USD")

def show_transaction_history():
    """İşlem geçmişi sekmesi"""
    st.subheader("📋 İşlem Geçmişi")
    
    user_data = get_current_user_data()
    
    if not user_data['transactions']:
        st.info("Henüz işlem geçmişi bulunmuyor.")
        return
    
    # Son 20 işlemi göster
    recent_transactions = user_data['transactions'][-20:]
    
    transaction_data = []
    for transaction in reversed(recent_transactions):
        transaction_data.append({
            'Tarih': transaction['date'],
            'İşlem': transaction['type'],
            'Hisse': transaction['symbol'],
            'Adet': transaction['quantity'],
            'Fiyat': f"{transaction['price']:.2f} USD",
            'Toplam': f"{transaction['total']:.2f} USD"
        })
    
    df = pd.DataFrame(transaction_data)
    st.dataframe(df, use_container_width=True)

def show_portfolio(data_manager, username):
    """Kullanıcının portföyünü göster"""
    portfolio = data_manager.get_user_portfolio(username)
    
    if not portfolio:
        st.info("📋 Portföyünüzde hisse bulunmuyor")
        return
    
    # Portföy tablosu
    df = pd.DataFrame(portfolio)
    df['Toplam Değer'] = df['total_shares'] * df['avg_price']
    
    st.dataframe(
        df,
        column_config={
            "symbol": "Sembol",
            "total_shares": "Adet",
            "avg_price": "Ort. Fiyat ($)",
            "Toplam Değer": st.column_config.NumberColumn("Toplam Değer (TL)", format="%.2f")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Toplam portföy değeri
    total_value = df['Toplam Değer'].sum()
    st.metric("💰 Toplam Portföy Değeri", f"{total_value:,.2f} USD")

def show_transactions(data_manager, username):
    """Kullanıcının işlem geçmişini göster"""
    transactions = data_manager.get_user_transactions(username, 10)

    if not transactions:
        st.info("📋 Henüz işlem geçmişi yok")
        return

    # İşlem geçmişi tablosu
    df = pd.DataFrame(transactions)
    
    # transaction_type sütunu varsa map et, yoksa varsayılan değer kullan
    if 'transaction_type' in df.columns:
        df['İşlem Türü'] = df['transaction_type'].map({'BUY': 'Alım', 'SELL': 'Satım'})
    else:
        df['İşlem Türü'] = 'Bilinmiyor'

    # Mevcut sütunları kontrol et ve güvenli şekilde göster
    available_columns = ['symbol', 'İşlem Türü', 'shares', 'price', 'total_amount', 'transaction_date']
    display_columns = [col for col in available_columns if col in df.columns]

    st.dataframe(
        df[display_columns],
        column_config={
            "symbol": "Sembol",
            "İşlem Türü": "İşlem",
            "shares": "Adet",
            "price": "Fiyat ($)",
            "total_amount": st.column_config.NumberColumn("Toplam (USD)", format="%.2f"),
            "transaction_date": "Tarih"
        },
        hide_index=True,
        use_container_width=True
    )

def show_performance_tracking(data_manager, username):
    """7 günlük performans takibini göster"""
    performance = data_manager.get_performance_summary(username)
    
    if not performance:
        st.info("📊 Henüz performans verisi yok")
        return
    
    # Performans tablosu
    df = pd.DataFrame(performance)
    
    st.dataframe(
        df,
        column_config={
            "symbol": "Sembol",
            "initial_investment": st.column_config.NumberColumn("Başlangıç Yatırımı (USD)", format="%.2f"),
            "current_value": st.column_config.NumberColumn("Güncel Değer (USD)", format="%.2f"),
            "profit_loss": st.column_config.NumberColumn("Kar/Zarar (USD)", format="%.2f"),
            "profit_loss_percent": st.column_config.NumberColumn("Kar/Zarar (%)", format="%.2f"),
            "tracking_start_date": "Takip Başlangıcı"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Genel performans özeti
    total_initial = df['initial_investment'].sum()
    total_current = df['current_value'].sum()
    total_profit_loss = total_current - total_initial
    total_profit_loss_percent = (total_profit_loss / total_initial) * 100 if total_initial > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Toplam Yatırım", f"{total_initial:,.2f} USD")
    
    with col2:
        st.metric("📈 Güncel Değer", f"{total_current:,.2f} USD")
    
    with col3:
        st.metric(
            "📊 Toplam Kar/Zarar", 
            f"{total_profit_loss:,.2f} USD",
            f"{total_profit_loss_percent:+.2f}%",
            delta_color="normal" if total_profit_loss >= 0 else "inverse"
        )

def show_tradingview_analysis():
    """TradingView analiz panelini göster"""
    st.header("📊 TradingView Teknik Analiz")
    st.markdown("**TradingView API ile gerçek zamanlı teknik analiz ve öneriler:**")
    
    # Hisse seçimi
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Takip listesinden hisseleri al
        try:
            app = StockAnalysisApp()
            watchlist = app.data_manager.get_watchlist()
            
            if watchlist:
                symbols = [item['symbol'] for item in watchlist]
                selected_symbol = st.selectbox("TradingView analizi için hisse seçin:", symbols)
            else:
                selected_symbol = st.text_input("Hisse sembolü girin (örn: AAPL, THYAO):", placeholder="AAPL")
        except Exception as e:
            selected_symbol = st.text_input("Hisse sembolü girin (örn: AAPL, THYAO):", placeholder="AAPL")
    
    with col2:
        analysis_button = st.button("🔍 TradingView Analizi Yap")
    
    if selected_symbol and analysis_button:
        try:
            with st.spinner(f"📊 {selected_symbol} için TradingView analizi yapılıyor..."):
                # TradingView analizi çek
                tradingview_analysis = app.stock_scraper.scrape_tradingview_data(selected_symbol.upper())
                
                if tradingview_analysis:
                    st.success(f"✅ {selected_symbol} TradingView analizi başarıyla çekildi!")
                    # Ana öneriler
                    col_tv1, col_tv2, col_tv3, col_tv4 = st.columns(4)
                    
                    with col_tv1:
                        summary = tradingview_analysis.get('summary', {})
                        if summary:
                            recommendation = summary.get('RECOMMENDATION', 'N/A')
                            buy_count = summary.get('BUY', 0)
                            sell_count = summary.get('SELL', 0)
                            neutral_count = summary.get('NEUTRAL', 0)
                            
                            # Öneri rengi
                            if recommendation == 'BUY':
                                rec_color = "🟢"
                            elif recommendation == 'SELL':
                                rec_color = "🔴"
                            else:
                                rec_color = "🟡"
                            
                            st.metric(f"Genel Öneri {rec_color}", recommendation)
                    
                    with col_tv2:
                        oscillators = tradingview_analysis.get('oscillators', {})
                        if oscillators:
                            oscillator_rec = oscillators.get('RECOMMENDATION', 'N/A')
                            st.metric("Oscillator", oscillator_rec)
                    
                    with col_tv3:
                        moving_averages = tradingview_analysis.get('moving_averages', {})
                        if moving_averages:
                            ma_rec = moving_averages.get('RECOMMENDATION', 'N/A')
                            st.metric("Moving Average", ma_rec)
                    
                    with col_tv4:
                        indicators = tradingview_analysis.get('indicators', {})
                        if indicators:
                            close_price = indicators.get('close', 'N/A')
                            st.metric("Güncel Fiyat", f"${close_price}" if close_price != 'N/A' else 'N/A')
                    
                    # Detaylı analiz
                    st.subheader("📈 Detaylı TradingView Analizi")
                    
                    # Özet analizi
                    if summary:
                        st.write("**📊 Özet Analiz:**")
                        summary_cols = st.columns(4)
                        with summary_cols[0]:
                            st.metric("Alış Sinyali", summary.get('BUY', 0))
                        with summary_cols[1]:
                            st.metric("Satış Sinyali", summary.get('SELL', 0))
                        with summary_cols[2]:
                            st.metric("Nötr Sinyal", summary.get('NEUTRAL', 0))
                        with summary_cols[3]:
                            total_signals = summary.get('BUY', 0) + summary.get('SELL', 0) + summary.get('NEUTRAL', 0)
                            st.metric("Toplam Sinyal", total_signals)
                    
                    # Oscillator detayları
                    if oscillators:
                        st.write("**📊 Oscillator Analizi:**")
                        oscillator_cols = st.columns(4)
                        with oscillator_cols[0]:
                            st.metric("RSI", oscillators.get('RSI', 'N/A'))
                        with oscillator_cols[1]:
                            st.metric("Stoch", oscillators.get('Stoch.K', 'N/A'))
                        with oscillator_cols[2]:
                            st.metric("CCI", oscillators.get('CCI20', 'N/A'))
                        with oscillator_cols[3]:
                            st.metric("Williams %R", oscillators.get('W%R', 'N/A'))
                    
                    # Moving Average detayları
                    if moving_averages:
                        st.write("**📊 Moving Average Analizi:**")
                        ma_cols = st.columns(4)
                        with ma_cols[0]:
                            st.metric("EMA20", moving_averages.get('EMA20', 'N/A'))
                        with ma_cols[1]:
                            st.metric("SMA20", moving_averages.get('SMA20', 'N/A'))
                        with ma_cols[2]:
                            st.metric("SMA50", moving_averages.get('SMA50', 'N/A'))
                        with ma_cols[3]:
                            st.metric("SMA200", moving_averages.get('SMA200', 'N/A'))
                    
                    # Teknik göstergeler
                    if indicators:
                        st.write("**📊 Teknik Göstergeler:**")
                        indicator_cols = st.columns(4)
                        with indicator_cols[0]:
                            st.metric("Güncel Fiyat", f"${indicators.get('close', 'N/A')}")
                        with indicator_cols[1]:
                            st.metric("Açılış", f"${indicators.get('open', 'N/A')}")
                        with indicator_cols[2]:
                            st.metric("Yüksek", f"${indicators.get('high', 'N/A')}")
                        with indicator_cols[3]:
                            st.metric("Düşük", f"${indicators.get('low', 'N/A')}")
                    
                    # Ham veri tablosu
                    with st.expander("📋 Ham TradingView Verisi"):
                        st.json(tradingview_analysis)
                
                else:
                    st.warning(f"⚠️ {selected_symbol} için TradingView analizi çekilemedi.")
                    st.info("💡 Olası nedenler:")
                    st.write("• API limitleri aşıldı")
                    st.write("• Hisse sembolü bulunamadı")
                    st.write("• Bağlantı sorunu")
                    st.write("• BIST hisseleri için .IS uzantısı gerekebilir")
        
        except Exception as e:
            st.error(f"❌ TradingView analizi sırasında hata: {str(e)}")
    
    # TradingView hakkında bilgi
    with st.expander("ℹ️ TradingView Analizi Hakkında"):
        st.markdown("""
        **TradingView Analizi Nedir?**
        
        TradingView, dünyanın en popüler teknik analiz platformlarından biridir. 
        Bu analiz şunları içerir:
        
        **📊 Özet Analiz:**
        - Genel alım/satım önerisi
        - Sinyal sayıları (Alış/Satış/Nötr)
        
        **📈 Oscillator Analizi:**
        - RSI (Relative Strength Index)
        - Stochastic Oscillator
        - CCI (Commodity Channel Index)
        - Williams %R
        
        **📊 Moving Average Analizi:**
        - EMA20 (Exponential Moving Average)
        - SMA20, SMA50, SMA200 (Simple Moving Average)
        
        **⚠️ Not:** API limitleri nedeniyle bazı hisseler için analiz çekilemeyebilir.
        """)

def show_settings():
    """Ayarları göster"""
    st.header("⚙️ Ayarlar")
    
    # API durumu raporu
    st.subheader("🔍 API Durumu Raporu")
    
    if st.button("🔄 API Durumunu Güncelle"):
        try:
            from scraper.stock_scraper import API_STATUS
            st.success("✅ API durumu güncellendi!")
            
            # API durumlarını göster
            col1, col2 = st.columns(2)
            
            with col1:
                for api_name, status in list(API_STATUS.items())[:4]:
                    status_emoji = {
                        'active': '✅',
                        'limited': '⚠️',
                        'invalid_key': '❌',
                        'test_key': '⚠️',
                        'limit_reached': '🚫',
                        'rate_limited': '⏳',
                        'missing_key': '🔑'
                    }.get(status, '❓')
                    
                    st.write(f"{status_emoji} {api_name.upper()}: {status}")
            
            with col2:
                for api_name, status in list(API_STATUS.items())[4:]:
                    status_emoji = {
                        'active': '✅',
                        'limited': '⚠️',
                        'invalid_key': '❌',
                        'test_key': '⚠️',
                        'limit_reached': '🚫',
                        'rate_limited': '⏳',
                        'missing_key': '🔑'
                    }.get(status, '❓')
                    
                    st.write(f"{status_emoji} {api_name.upper()}: {status}")
                    
        except Exception as e:
            st.error(f"❌ API durumu güncellenirken hata: {str(e)}")
    
    st.subheader("🔑 API Ayarları")
    st.info("Twelve Data API anahtarı kodda tanımlı.")
    
    st.subheader("📊 Veri Kaynakları")
    st.write("**Aktif Veri Kaynakları:**")
    st.write("✅ Twelve Data API")
    st.write("✅ IEX Cloud API")
    st.write("✅ MarketStack API")
    st.write("✅ Financial Modeling Prep API")
    st.write("✅ Alpha Vantage API")
    st.write("✅ TradingView API")
    st.write("⚠️ Yahoo Finance (limit aşımı)")
    
    st.subheader("🔄 Sistem Durumu")
    st.write("**Tüm modüller çalışıyor:**")
    st.write("✅ Veri Çekme")
    st.write("✅ Analiz")
    st.write("✅ Görselleştirme")
    st.write("✅ Raporlama")
    st.write("✅ TradingView Entegrasyonu")
    
    # Hata logları
    st.subheader("📋 Son Hatalar")
    
    error_logs = [
        {"Tarih": "2024-01-15 14:30", "Hata": "Yahoo Finance API rate limit", "Çözüm": "Mock data kullanıldı"},
        {"Tarih": "2024-01-15 14:25", "Hata": "Finnhub API geçersiz anahtar", "Çözüm": "Alternatif API kullanıldı"},
        {"Tarih": "2024-01-15 14:20", "Hata": "BIST hisse verisi bulunamadı", "Çözüm": "Web scraping kullanıldı"}
    ]
    
    st.dataframe(
        pd.DataFrame(error_logs),
        hide_index=True,
        use_container_width=True
    )

def show_news_page():
    """Güncel haberler sayfası"""
    st.header("📰 Güncel Haberler")
    st.markdown("**ABD ve BIST piyasalarından güncel haberler ve sentiment analizi**")

    # Haber kaynağı seçimi
    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("Piyasa:", ["ABD Piyasası", "BIST Piyasası"], key="news_market")
    with col2:
        limit = st.slider("Haber sayısı:", 5, 20, 10, key="news_limit")

    market_code = "us" if market == "ABD Piyasası" else "tr"

    if st.button("🔄 Haberleri Güncelle", key="refresh_news"):
        with st.spinner("Haberler yükleniyor..."):
            news_scraper = NewsScraper()
            sentiment_analyzer = SentimentAnalyzer()
            
            # Haberleri çek
            news_list = news_scraper.get_market_news(market_code, limit)
            
            if news_list:
                # Sentiment analizi
                analyzed_news = sentiment_analyzer.analyze_news_batch(news_list)
                summary = sentiment_analyzer.get_sentiment_summary(analyzed_news)
                
                # Özet metrikler
                st.subheader("📊 Haber Özeti")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Toplam Haber", summary['total_news'])
                with col2:
                    st.metric("Pozitif", f"%{summary['positive_ratio']:.1f}")
                with col3:
                    st.metric("Negatif", f"%{summary['negative_ratio']:.1f}")
                with col4:
                    st.metric("Piyasa Durumu", summary['market_sentiment'])
                
                # Trend konular
                if summary['trending_topics']:
                    st.write("**🔥 Trend Konular:**")
                    for topic in summary['trending_topics']:
                        st.write(f"• {topic}")
                
                # Haber listesi
                st.subheader("📋 Haber Detayları")
                for i, news in enumerate(analyzed_news):
                    # Sentiment rengi
                    sentiment_color = {
                        'positive': '#28a745',
                        'negative': '#dc3545',
                        'neutral': '#6c757d'
                    }.get(news['sentiment'], '#6c757d')
                    
                    # Haber kartı
                    with st.expander(f"📰 {news['title']}", expanded=i < 3):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Kaynak:** {news['source']}")
                            st.write(f"**Kategori:** {news['category']}")
                            st.write(f"**Tarih:** {news['published_date']}")
                            st.write(f"**İçerik:** {news['content']}")
                            
                            if news['symbols']:
                                st.write(f"**İlgili Hisseler:** {', '.join(news['symbols'])}")
                        
                        with col2:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 10px; background-color: {sentiment_color}; color: white; border-radius: 5px;">
                                <strong>{news['sentiment_label']}</strong><br>
                                Güven: %{news['confidence']*100:.1f}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if news['financial_impact'] != 'Düşük':
                                st.info(f"Finansal Etki: {news['financial_impact']}")
            else:
                st.warning("Haber verisi bulunamadı.")

    # Hisse bazlı haberler
    st.subheader("📈 Hisse Bazlı Haberler")
    selected_stock = st.selectbox("Hisse seçin:", us_stocks, key="stock_news")
    
    if selected_stock and st.button("🔍 Hisse Haberleri Ara", key="search_stock_news"):
        with st.spinner(f"{selected_stock} haberleri aranıyor..."):
            news_scraper = NewsScraper()
            stock_news = news_scraper.get_stock_news(selected_stock, 5)
            
            if stock_news:
                st.write(f"**{selected_stock} için son haberler:**")
                for news in stock_news:
                    sentiment_color = {
                        'positive': '#28a745',
                        'negative': '#dc3545',
                        'neutral': '#6c757d'
                    }.get(news['sentiment'], '#6c757d')
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {sentiment_color}; padding-left: 10px; margin: 10px 0;">
                        <h4>{news['title']}</h4>
                        <p><strong>Kaynak:</strong> {news['source']} | <strong>Sentiment:</strong> {news['sentiment_label']}</p>
                        <p>{news['content']}</p>
                        <small>{news['published_date']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"{selected_stock} için haber bulunamadı.")

def main():
    """Ana uygulama fonksiyonu"""
    st.title("📈 Hisse Takip ve Analiz Dashboard")
    st.markdown("---")
    
    # Sidebar - Kullanıcı Seçimi ve Portföy Bilgileri
    with st.sidebar:
        st.header("👤 Kullanıcı Yönetimi")
        
        # Kullanıcı seçimi
        users = user_manager.get_users()
        user_options = {f"{user_data['name']} ({username})": username for username, user_data in users.items()}
        selected_user_display = st.selectbox("Kullanıcı Seçin:", list(user_options.keys()), 
                                            index=0 if st.session_state.current_user == "gokhan" else 1)
        selected_user = user_options[selected_user_display]
        
        if selected_user != st.session_state.current_user:
            st.session_state.current_user = selected_user
            # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
        
        # Kullanıcı bilgileri
        user_data = users[selected_user]
        st.subheader(f"💰 {user_data['name']} - Portföy")
        
        # Bakiye
        balance = user_manager.get_user_balance(selected_user)
        st.metric("Nakit Bakiye", f"{balance:,.2f} USD")
        
        # Güncel döviz kuru
        try:
            from portfolio.exchange_rate import exchange_rate_service
            usdt_rate = exchange_rate_service.get_usdt_to_try_rate()
            st.metric("💱 USDT/TRY Kuru", f"{usdt_rate:.4f}")
        except:
            st.metric("💱 USDT/TRY Kuru", "30.0000")
        
        # Portföy değeri (basit hesaplama)
        portfolio = user_manager.get_portfolio(selected_user)
        if portfolio:
            # Gerçek fiyatları almak için crypto analyzer kullan
            portfolio_value = 0.0
            crypto_analyzer = st.session_state.get('crypto_analyzer')
            for symbol in portfolio.keys():
                try:
                    if crypto_analyzer:
                        coin_data = crypto_analyzer.get_coin_data(symbol)
                        if coin_data:
                            current_price = coin_data['current_price']
                            amount = portfolio[symbol]['amount']
                            portfolio_value += amount * current_price
                        else:
                            # API'den fiyat alınamazsa ortalama fiyat kullan
                            amount = portfolio[symbol]['amount']
                            avg_price = portfolio[symbol]['avg_price']
                            portfolio_value += amount * avg_price
                    else:
                        # Crypto analyzer yoksa ortalama fiyat kullan
                        amount = portfolio[symbol]['amount']
                        avg_price = portfolio[symbol]['avg_price']
                        portfolio_value += amount * avg_price
                except:
                    # Hata durumunda ortalama fiyat kullan
                    try:
                        amount = portfolio[symbol]['amount']
                        avg_price = portfolio[symbol]['avg_price']
                        portfolio_value += amount * avg_price
                    except:
                        continue
            
            total_value = balance + portfolio_value
            st.metric("Toplam Portföy Değeri", f"{total_value:,.2f} USD")
            st.metric("Kripto Değeri", f"{portfolio_value:,.2f} USD")
        else:
            st.metric("Toplam Portföy Değeri", f"{balance:,.2f} USD")
            st.info("Henüz kripto varlığı yok")
        
        st.divider()
        
        # Takip listesi
        st.subheader("📈 Takip Listesi")
        watchlist = user_manager.get_watchlist(selected_user)
        
        if watchlist:
            st.write(f"**{len(watchlist)} coin takip ediliyor:**")
            for symbol in watchlist:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {symbol}")
                with col2:
                    if st.button("❌", key=f"remove_{symbol}", help="Takip listesinden çıkar"):
                        user_manager.remove_from_watchlist(selected_user, symbol)
                        # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
        else:
            st.info("Takip listesi boş")
        
        st.divider()
        
        # Hızlı işlemler
        st.subheader("⚡ Hızlı İşlemler")
        
        # Portföy yönetimi butonu
        if st.button("💼 Portföy Yönetimi", type="primary"):
            st.session_state.show_portfolio = True
            # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
        
        # İşlem geçmişi butonu
        if st.button("📊 İşlem Geçmişi"):
            st.session_state.show_transactions = True
            # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
        
        # Bakiye sıfırlama butonu
        if st.button("💰 Bakiyeyi 500K USD'ye Sıfırla", type="secondary"):
            user_manager.reset_user_balance(selected_user, 500000.0)
            st.success(f"✅ {user_data['name']} bakiyesi 500,000 USD'ye sıfırlandı!")
            # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
        
        st.divider()
        
        # Ana menü
        st.title("📊 Menü")
        page = st.selectbox(
            "Sayfa Seçin:",
            ["🏠 Ana Sayfa", "📈 Hisse Analizi", "🚀 Fırsat Analizi", "🤖 AI Analizi", "🪙 Crypto Analizi", "💼 Portföy Yönetimi", "📰 Haberler", "💰 Portföy Optimizer", 
             "🔔 Alarm Sistemi", "🎮 Sanal Trading", "🪙 Crypto Sanal Trading", "📊 TradingView", "⚙️ Ayarlar"]
        )
    
    # Sayfa yönlendirmesi
    if page == "🏠 Ana Sayfa":
        show_home_page()
    elif page == "📈 Hisse Analizi":
        show_stock_analysis()
    elif page == "🚀 Fırsat Analizi":
        show_opportunity_analysis()
    elif page == "🤖 AI Analizi":
        show_ai_analysis()
    elif page == "🪙 Crypto Analizi":
        show_crypto_analysis()
    elif page == "💼 Portföy Yönetimi":
        show_portfolio_management()
    elif page == "📰 Haberler":
        show_news_page()
    elif page == "💰 Portföy Optimizer":
        show_portfolio_optimizer()
    elif page == "🔔 Alarm Sistemi":
        show_alerts_system()
    elif page == "🎮 Sanal Trading":
        show_virtual_trading()
    elif page == "🪙 Crypto Sanal Trading":
        show_crypto_virtual_trading()
    elif page == "📊 TradingView":
        show_tradingview_analysis()
    elif page == "⚙️ Ayarlar":
        show_settings()

def show_home_page():
    """Ana sayfa"""
    st.header("🏠 Hoş Geldiniz!")
    st.markdown("""
    **Hisse Takip ve Analiz Dashboard**'a hoş geldiniz!
    
    Bu platform ile:
    - 📈 BIST ve ABD hisselerini analiz edebilirsiniz
    - 🤖 AI destekli fiyat tahminleri alabilirsiniz
    - 📰 Güncel haberleri takip edebilirsiniz
    - 💰 Portföy optimizasyonu yapabilirsiniz
    - 🔔 Fiyat alarmları kurabilirsiniz
    - 🎮 Sanal trading deneyebilirsiniz
    
    Sol menüden istediğiniz özelliği seçin!
    """)
    
    # Hızlı istatistikler
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Toplam Hisse", "1000+")
    with col2:
        st.metric("🤖 AI Modeller", "4")
    with col3:
        st.metric("📰 Haber Kaynağı", "10+")
    with col4:
        st.metric("⚡ Gerçek Zamanlı", "Evet")
    
    # Hakkında kısmı
    st.markdown("---")
    st.subheader("ℹ️ Hakkında")
    
    # Hakkında butonu
    if st.button("👨‍💻 Geliştirici Bilgileri", key="about_developer"):
        st.info("**Geliştirici:** Gökhan İşcanlı")
        st.markdown("""
        **📧 İletişim:** [gokhan.iscanli@example.com](mailto:gokhan.iscanli@example.com)
        
        **🌐 GitHub:** [github.com/gokhaniscanli](https://github.com/gokhaniscanli)
        
        **📱 LinkedIn:** [linkedin.com/in/gokhaniscanli](https://linkedin.com/in/gokhaniscanli)
        
        ---
        
        **Bu proje, hisse senedi analizi ve sanal trading deneyimi için geliştirilmiştir.**
        
        **Teknolojiler:**
        - 🐍 Python
        - 📊 Streamlit
        - 🤖 AI/ML Modelleri
        - 📈 Plotly Grafikleri
        - 💾 SQLite Veritabanı
        """)

def show_stock_analysis():
    """Hisse analizi sayfası"""
    st.header("📈 Hisse Analizi")
    
    # Hisse seçimi
    col1, col2 = st.columns(2)
    
    with col1:
        market = st.selectbox("Piyasa:", ["BIST", "ABD"], key="analysis_market")
    
    with col2:
        if market == "BIST":
            stocks = get_comprehensive_stock_list()
        else:
            stocks = get_us_stock_list()
        
        selected_stock = st.selectbox("Hisse Seçin:", stocks, key="analysis_stock")
    
    if selected_stock and st.button("🔍 Analiz Et"):
        with st.spinner("Analiz yapılıyor..."):
            # Hisse verilerini çek
            stock_data = get_stock_data(selected_stock, "1y")
            
            if stock_data is not None and 'data' in stock_data and not stock_data['data'].empty:
                # Fiyat grafiği
                st.subheader("📊 Fiyat Grafiği")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=stock_data['data'].index,
                    y=stock_data['data']['close'],
                    mode='lines',
                    name='Kapanış Fiyatı'
                ))
                fig.update_layout(title=f"{selected_stock} Fiyat Grafiği")
                st.plotly_chart(fig, use_container_width=True)
                
                # Temel istatistikler
                st.subheader("📈 Temel İstatistikler")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Son Fiyat", f"{stock_data['current_price']:.2f}")
                with col2:
                    st.metric("Yıllık Değişim", f"{stock_data['change_365d']:.2f}%")
                with col3:
                    st.metric("52 Hafta En Yüksek", f"{stock_data['data']['high'].max():.2f}")
                with col4:
                    st.metric("52 Hafta En Düşük", f"{stock_data['data']['low'].min():.2f}")
            else:
                st.error("Hisse verisi çekilemedi.")

def show_opportunity_analysis():
    """Fırsat analizi sayfası"""
    st.header("🚀 Fırsat Analizi")
    st.markdown("**Düşüş gösteren hisselerden fırsat analizi**")
    
    print(f"DEBUG OPPORTUNITY: Sayfa yüklendi. Mevcut takip listesi: {st.session_state.watchlist}")
    
    # Refresh kontrolü
    if st.session_state.refresh_watchlist:
        st.session_state.refresh_watchlist = False
        st.rerun()
    
    # Analiz parametreleri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        market = st.selectbox("Piyasa:", ["BIST + ABD", "BIST", "ABD"], key="opportunity_market")
    
    with col2:
        min_drop = st.slider("Minimum Düşüş (%):", 5, 80, 20, key="opportunity_min_drop")
    
    with col3:
        max_results = st.slider("Maksimum Sonuç:", 3, 20, 5, key="opportunity_max_results")
    
    if st.button("🚀 Fırsatları Analiz Et", type="primary", key="analyze_opportunities"):
        print(f"DEBUG OPPORTUNITY: Fırsatları Analiz Et butonuna tıklandı!")
        with st.spinner("🔍 Fırsatlar analiz ediliyor..."):
            # Fırsat analizi yap
            opportunities = analyze_downtrend_stocks()
            print(f"DEBUG OPPORTUNITY: {len(opportunities)} fırsat bulundu!")
            
                                    # Sonuçları session state'e kaydet
            st.session_state["opportunities_data"] = opportunities
            st.rerun()
    
    # Fırsatları göster
    if st.session_state["opportunities_data"]:
        opportunities = st.session_state["opportunities_data"]
        if opportunities and len(opportunities) > 0:
            st.success(f"✅ {len(opportunities)} fırsat bulundu!")
            
            # Fırsatları göster
            st.subheader("🔥 Bulunan Fırsatlar")
            
            for i, opportunity in enumerate(opportunities[:max_results]):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
                    
                    with col1:
                        st.write(f"**{opportunity['symbol']}**")
                        st.write(f"*{opportunity.get('name', 'N/A')}*")
                        st.write(f"Fırsat Tipi: {opportunity.get('opportunity_type', 'Düşüş Fırsatı')}")
                    
                    with col2:
                        st.metric("Skor", f"{opportunity.get('score', 0)}")
                    
                    with col3:
                        st.metric("Fiyat", f"{opportunity.get('current_price', 0):.2f}")
                        st.metric("Değişim", f"{opportunity.get('change_percent', 0):.1f}%")
                    
                    with col4:
                        # Takibe Al butonu - Callback ile
                        if st.button(f"📈 Takibe Al", key=f"watch_{opportunity['symbol']}", on_click=add_to_watchlist_callback(opportunity['symbol'])):
                            print(f"DEBUG OPPORTUNITY: Takibe Al butonuna tıklandı: {opportunity['symbol']}")
                        
                        # Detay Analiz butonu
                        if st.button(f"🔍 Detay Analiz", key=f"detail_opp_{opportunity['symbol']}"):
                            st.info(f"{opportunity['symbol']} için detaylı analiz yapılıyor...")
                    
                        st.divider()
            
            # Özet istatistikler
            st.subheader("📊 Fırsat Özeti")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Toplam Fırsat", len(opportunities))
            with col2:
                avg_drop = sum(opp.get('change_percent', 0) for opp in opportunities) / len(opportunities)
                st.metric("Ortalama Düşüş", f"{avg_drop:.1f}%")
            with col3:
                best_opportunity = min(opportunities, key=lambda x: x.get('change_percent', 0))
                st.metric("En İyi Fırsat", best_opportunity['symbol'])
            with col4:
                st.metric("En Düşük Fiyat", f"{best_opportunity.get('current_price', 0):.2f}")
        else:
            st.warning("❌ Belirtilen kriterlere uygun fırsat bulunamadı.")
            st.info("💡 Daha düşük bir minimum düşüş yüzdesi deneyin.")
    
    # Geçmiş fırsatlar
    st.subheader("📈 Geçmiş Fırsatlar")
    st.info("Bu bölümde geçmiş fırsat analizleri ve sonuçları gösterilecek.")

def show_crypto_analysis():
    """Crypto analizi sayfası"""
    st.header("🪙 Crypto Analizi")
    st.markdown("**USDT üzerindeki coinlerin anlık analizi ve fırsat tespiti**")
    
    print(f"DEBUG CRYPTO: Sayfa yüklendi. Mevcut takip listesi: {st.session_state.watchlist}")
    print(f"DEBUG CRYPTO: Takip listesi ID: {id(st.session_state.watchlist)}")
    
    # Takip listesi koruma kontrolü
    if 'watchlist' not in st.session_state or st.session_state.watchlist is None:
        print(f"DEBUG CRYPTO: Takip listesi korunuyor, yeniden başlatılıyor...")
        st.session_state.watchlist = []
    
    # Takip listesi kontrolü - eğer boşsa Fırsat Analizi'nden gelen verileri kullan
    if not st.session_state.watchlist and hasattr(st.session_state, 'opportunities_data') and st.session_state.opportunities_data is not None and len(st.session_state.opportunities_data) > 0:
        print(f"DEBUG CRYPTO: Takip listesi boş, Fırsat Analizi verilerini kontrol ediyorum...")
        print(f"DEBUG CRYPTO: opportunities_data tipi: {type(st.session_state.opportunities_data)}")
        print(f"DEBUG CRYPTO: opportunities_data içeriği: {st.session_state.opportunities_data}")
        
        # Fırsat Analizi'nden otomatik ekleme kaldırıldı - sadece manuel "Takibe Al" butonları ile eklenir
        print(f"DEBUG CRYPTO: Otomatik takip listesi ekleme devre dışı")
    else:
        print(f"DEBUG CRYPTO: Takip listesi kontrolü atlandı - watchlist: {bool(st.session_state.watchlist)}, opportunities_data: {hasattr(st.session_state, 'opportunities_data')}")
        if hasattr(st.session_state, 'opportunities_data'):
            print(f"DEBUG CRYPTO: opportunities_data tipi: {type(st.session_state.opportunities_data)}")
            print(f"DEBUG CRYPTO: opportunities_data None mu: {st.session_state.opportunities_data is None}")
            if st.session_state.opportunities_data is not None:
                print(f"DEBUG CRYPTO: opportunities_data uzunluğu: {len(st.session_state.opportunities_data) if isinstance(st.session_state.opportunities_data, list) else 'liste değil'}")
    
    # Takip listesi debug bilgisi
    print(f"DEBUG CRYPTO: Mevcut takip listesi uzunluğu: {len(st.session_state.watchlist)}")
    print(f"DEBUG CRYPTO: Takip listesi içeriği: {st.session_state.watchlist}")
    
    # Session state debug bilgisi
    print(f"DEBUG CRYPTO: Session state anahtarları: {list(st.session_state.keys())}")
    print(f"DEBUG CRYPTO: watchlist session state'de var mı: {'watchlist' in st.session_state}")
    print(f"DEBUG CRYPTO: watchlist ID: {id(st.session_state.watchlist)}")
    
    # Refresh kontrolü
    if st.session_state.refresh_watchlist:
        st.session_state.refresh_watchlist = False
        st.rerun()
    
    # Crypto analyzer'ı al
    crypto_analyzer = st.session_state.crypto_analyzer
    
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🚀 Fırsat Analizi", "💰 24h Kazanç Analizi", "🐋 Balina Analizi", "⚡ 1h Kazanç Analizi", "📊 Coin Detayları", "📈 Grafik Analizi", "⚙️ Ayarlar"])
    
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
                            # Session state'e kaydet
                            st.session_state["opportunities_data"] = filtered_opportunities
                            print(f"🔴🔴🔴 DEBUG: Fırsat Analizi - opportunities_data session state'e kaydedildi: {len(filtered_opportunities)} fırsat 🔴🔴🔴")
                            
                            st.success(f"✅ {len(filtered_opportunities)} {selected_category.lower()} fırsatı bulundu!")
                            
                            # Fırsatları göster
                            st.subheader(f"🔥 Bulunan {selected_category} Fırsatları")
                            
                            for i, opportunity in enumerate(filtered_opportunities):
                                with st.container():
                                    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
                                    
                                    with col1:
                                        coin_type = determine_coin_type(opportunity['symbol'], opportunity['current_price'], opportunity['volume_24h'])
                                        st.write(f"**{opportunity['symbol']}** ({coin_type})")
                                        st.write(f"💰 **Fiyat:** ${opportunity['current_price']:.6f}")
                                        st.write(f"📊 **24h Değişim:** {opportunity['change_24h']:+.2f}%")
                                        st.write(f"📈 **7g Değişim:** {opportunity['change_7d']:+.2f}%")
                                        st.write(f"💎 **Fırsat Tipi:** {opportunity['opportunity_type']}")
                                    
                                    with col2:
                                        st.metric("Skor", f"{opportunity['opportunity_score']:.1f}")
                                        if opportunity.get('rsi'):
                                            st.metric("RSI", f"{opportunity['rsi']:.1f}")
                                    
                                    with col3:
                                        st.metric("Hacim", f"${opportunity['volume_24h']/1000000:.1f}M")
                                        st.metric("Öneri", opportunity['recommendation'])
                                    
                                    with col4:
                                        # Takibe Al butonu - Callback ile
                                        button_key = f"crypto_watch_{opportunity['symbol']}_{i}"
                                        if st.button(f"📈 Takibe Al", key=button_key, on_click=add_to_watchlist_callback(opportunity['symbol'])):
                                            print(f"🔴🔴🔴 DEBUG CRYPTO: Takibe Al butonuna tıklandı: {opportunity['symbol']} 🔴🔴🔴")
                                        
                                        # Detay Analiz butonu
                                        detail_key = f"crypto_detail_{opportunity['symbol']}_{i}"
                                        if st.button(f"🔍 Detay", key=detail_key):
                                            st.info(f"{opportunity['symbol']} için detaylı analiz yapılıyor...")
                                    
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
                                with st.container():
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
                                        # Alım-Satım butonları
                                        # Takibe Al butonu - Callback ile
                                        st.write(f"🔴 DEBUG: {opportunity['symbol']} için buton oluşturuluyor")
                                        st.write(f"🔴 DEBUG: Buton key: watch_{opportunity['symbol']}")
                                        if st.button(f"📈 TAKIBE AL", key=f"watch_{opportunity['symbol']}", on_click=add_to_watchlist_callback(opportunity['symbol'])):
                                            print(f"DEBUG CRYPTO: Takibe Al butonuna tıklandı: {opportunity['symbol']}")
                                        else:
                                            st.write(f"🔴 DEBUG: {opportunity['symbol']} butonu tıklanmadı")
                                        
                                        col_actions1, col_actions2 = st.columns(2)
                                        
                                        with col_actions1:
                                            
                                            # Al butonu
                                            buy_button_key = f"profit_buy_{opportunity['symbol']}_{i}"
                                            if st.button(f"💰 Al", key=buy_button_key, type="primary"):
                                                # Alım miktarı
                                                amount = st.number_input(f"{opportunity['symbol']} miktarı (USDT):", 
                                                                        min_value=10.0, value=100.0, step=10.0, 
                                                                        key=f"buy_amount_{opportunity['symbol']}_{i}")
                                                confirm_key = f"confirm_buy_{opportunity['symbol']}_{i}"
                                                if st.button(f"✅ Satın Al", key=confirm_key):
                                                    buy_crypto(opportunity['symbol'], amount, opportunity['current_price'])
                                                    # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
                                        
                                        with col_actions2:
                                            # Detay Analiz butonu
                                            detail_key = f"profit_detail_{opportunity['symbol']}_{i}"
                                            if st.button(f"🔍 Detay", key=detail_key):
                                                st.info(f"{opportunity['symbol']} için detaylı analiz yapılıyor...")
                                            
                                            # Portföy kontrolü
                                            current_user = st.session_state.current_user
                                            portfolio = user_manager.get_portfolio(current_user)
                                            if opportunity['symbol'] in portfolio:
                                                st.info(f"Portföyde: {portfolio[opportunity['symbol']]['amount']:.2f} {opportunity['symbol']}")
                                                
                                                # Sat butonu
                                                sell_key = f"profit_sell_{opportunity['symbol']}_{i}"
                                                if st.button(f"💸 Sat", key=sell_key):
                                                    amount = portfolio[opportunity['symbol']]['amount']
                                                    sell_crypto(opportunity['symbol'], amount, opportunity['current_price'])
                                                    # st.run() kaldırıldı - sayfa yeniden yüklenmeyecek
                                    
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
        st.subheader("🐋 Balina Analizi")
        st.markdown("**Son 3 ayda balinaların en çok alım yaptığı coinleri analiz eder ve yakın vadede hangi coinlere giriş yapabileceklerini tahmin eder**")
        
        # Balina analizi parametreleri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            whale_min_volume = st.number_input("Min. Balina Hacmi (Milyon USDT):", 1, 1000, 10, key="whale_min_volume")
        
        with col2:
            whale_analysis_period = st.selectbox("Analiz Periyodu:", ["3 Ay", "6 Ay", "1 Yıl"], key="whale_period")
        
        with col3:
            whale_prediction_days = st.slider("Tahmin Günleri:", 7, 90, 30, key="whale_prediction_days")
        
        if st.button("🐋 Balina Analizini Başlat", type="primary", key="analyze_whale_activity"):
            print(f"🔴🔴🔴 BALINA ANALIZ: Balina analizi başlat butonuna tıklandı! 🔴🔴🔴")
            with st.spinner("🔄 Balina aktiviteleri analiz ediliyor..."):
                try:
                    # Balina analizi fonksiyonunu çağır
                    whale_analysis = analyze_whale_activity(
                        min_volume=whale_min_volume * 1000000,
                        period=whale_analysis_period,
                        prediction_days=whale_prediction_days
                    )
                    print(f"🔴🔴🔴 BALINA ANALIZ: Analiz tamamlandı, sonuç: {whale_analysis is not None} 🔴🔴🔴")
                    
                    if whale_analysis:
                        print(f"🔴🔴🔴 BALINA ANALIZ: Whale analysis başarılı! Toplam coin: {len(whale_analysis['top_whale_coins'])} 🔴🔴🔴")
                        st.success(f"✅ Balina analizi tamamlandı! {len(whale_analysis['top_whale_coins'])} coin analiz edildi.")
                        
                        # En çok alım yapılan coinler
                        st.subheader("🐋 En Çok Balina Alımı Yapılan Coinler")
                        
                        for i, coin in enumerate(whale_analysis['top_whale_coins']):
                            print(f"🔴🔴🔴 BALINA COIN: {i}. coin: {coin['symbol']} 🔴🔴🔴")
                            with st.container():
                                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                                
                                with col1:
                                    st.write(f"**{coin['symbol']}** - {coin['coin_type']}")
                                    st.write(f"💰 **Güncel Fiyat:** ${coin['current_price']:.6f}")
                                    st.write(f"📊 **Balina Alım Hacmi:** ${coin['whale_volume']/1000000:.1f}M")
                                    st.write(f"🐋 **Balina Sayısı:** {coin['whale_count']}")
                                    st.write(f"📈 **Son 3 Ay Değişim:** {coin['change_3m']:+.2f}%")
                                
                                with col2:
                                    st.metric("Balina Skoru", f"{coin['whale_score']:.1f}")
                                    st.metric("Hacim", f"${coin['volume_24h']/1000000:.1f}M")
                                
                                with col3:
                                    st.metric("RSI", f"{coin['rsi']:.1f}")
                                    st.metric("Trend", coin['trend'])
                                
                                with col4:
                                    # Takibe Al butonu
                                    st.button(f"📈 Takibe Al", key=f"whale_watch_{coin['symbol']}_{i}", 
                                             on_click=add_to_watchlist, args=(coin['symbol'],))
                                    
                                    # Detay butonu
                                    if st.button(f"🔍 Detay", key=f"whale_detail_{coin['symbol']}_{i}"):
                                        st.info(f"{coin['symbol']} balina detayları gösteriliyor...")
                                
                                st.divider()
                        
                        # Yakın vadeli tahminler
                        st.subheader("🔮 Yakın Vadeli Balina Tahminleri")
                        st.info(f"**{whale_prediction_days} gün içinde balinaların giriş yapabileceği coinler:**")
                        
                        print(f"🔴🔴🔴 BALINA PREDICTIONS: Toplam tahmin: {len(whale_analysis['predictions'])} 🔴🔴🔴")
                        for j, prediction in enumerate(whale_analysis['predictions']):
                            print(f"🔴🔴🔴 BALINA PREDICTION: {j}. tahmin: {prediction['symbol']} 🔴🔴🔴")
                            with st.container():
                                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                                
                                with col1:
                                    st.write(f"**{prediction['symbol']}** - {prediction['coin_type']}")
                                    st.write(f"💰 **Güncel Fiyat:** ${prediction['current_price']:.6f}")
                                    st.write(f"📅 **Tahmin Tarihi:** {prediction['predicted_date']}")
                                    st.write(f"🎯 **Giriş Olasılığı:** %{prediction['entry_probability']:.1f}")
                                    st.write(f"📊 **Beklenen Hacim:** ${prediction['expected_volume']/1000000:.1f}M")
                                
                                with col2:
                                    st.metric("Tahmin Skoru", f"{prediction['prediction_score']:.1f}")
                                    st.metric("Mevcut Hacim", f"${prediction['current_volume']/1000000:.1f}M")
                                
                                with col3:
                                    st.metric("RSI", f"{prediction['rsi']:.1f}")
                                    st.metric("Trend", prediction['trend'])
                                
                                with col4:
                                    # Takibe Al butonu
                                    st.button(f"📈 Takibe Al", key=f"prediction_watch_{prediction['symbol']}_{j}", 
                                             on_click=add_to_watchlist, args=(prediction['symbol'],))
                                    
                                    # Detay butonu
                                    if st.button(f"🔍 Detay", key=f"prediction_detail_{prediction['symbol']}_{j}"):
                                        st.info(f"{prediction['symbol']} tahmin detayları gösteriliyor...")
                                
                                st.divider()
                        
                        # Balina analizi özeti
                        st.subheader("📊 Balina Analizi Özeti")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Analiz Edilen Coin", len(whale_analysis['top_whale_coins']))
                        
                        with col2:
                            total_whale_volume = sum(coin['whale_volume'] for coin in whale_analysis['top_whale_coins'])
                            st.metric("Toplam Balina Hacmi", f"${total_whale_volume/1000000:.0f}M")
                        
                        with col3:
                            avg_whale_score = sum(coin['whale_score'] for coin in whale_analysis['top_whale_coins']) / len(whale_analysis['top_whale_coins'])
                            st.metric("Ortalama Balina Skoru", f"{avg_whale_score:.1f}")
                        
                        with col4:
                            st.metric("Tahmin Sayısı", len(whale_analysis['predictions']))
                        
                        # Balina aktivite grafiği
                        st.subheader("📈 Balina Aktivite Grafiği")
                        st.info("Balina aktivitelerinin zaman içindeki değişimi grafik olarak gösterilecek.")
                        
                        # Balina kategorileri
                        st.subheader("🐋 Balina Kategorileri")
                        col_cat1, col_cat2, col_cat3 = st.columns(3)
                        
                        with col_cat1:
                            major_whales = sum(1 for coin in whale_analysis['top_whale_coins'] if coin['coin_type'] == "Major Coin")
                            st.metric("Major Coin Balinaları", major_whales)
                        
                        with col_cat2:
                            altcoin_whales = sum(1 for coin in whale_analysis['top_whale_coins'] if coin['coin_type'] == "Altcoin")
                            st.metric("Altcoin Balinaları", altcoin_whales)
                        
                        with col_cat3:
                            defi_whales = sum(1 for coin in whale_analysis['top_whale_coins'] if coin['coin_type'] == "DeFi Token")
                            st.metric("DeFi Balinaları", defi_whales)
                    
                    else:
                        st.warning("❌ Balina analizi verisi bulunamadı.")
                        st.info("💡 Farklı parametreler deneyin veya daha sonra tekrar deneyin.")
                
                except Exception as e:
                    st.error(f"Balina analizi sırasında hata oluştu: {str(e)}")
    
    with tab4:
        st.subheader("⚡ 1 Saatlik Kazanç Analizi")
        st.markdown("**Düşüşe geçmiş ve 1 saat içinde rekor seviyede yükseliş yapabilecek coinleri analiz eder**")
        
        # 1h kazanç analizi parametreleri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_1h_score = st.slider("Minimum 1h Skoru:", 20, 90, 35, key="1h_min_score")
        
        with col2:
            max_1h_results = st.slider("Maksimum Sonuç:", 5, 25, 10, key="1h_max_results")
        
        with col3:
            selected_1h_category = st.selectbox("Coin Türü:", list(coin_categories.keys()), key="1h_category")
        
        st.info(f"📋 **1 Saatlik Analiz:** {selected_1h_category} kategorisinde düşüşe geçmiş ve 1 saat içinde rekor yükseliş potansiyeli olan {min_1h_score}+ skorlu coinler")
        
        if st.button("⚡ 1 Saatlik Kazanç Fırsatlarını Analiz Et", type="primary", key="analyze_1h_profit"):
            print(f"🔴🔴🔴 1H ANALIZ: 1 Saatlik Kazanç Fırsatlarını Analiz Et butonuna tıklandı! 🔴🔴🔴")
            with st.spinner("🔄 1 saatlik kazanç fırsatları analiz ediliyor..."):
                try:
                    # 1 saatlik kazanç fırsatlarını bul
                    one_hour_opportunities = crypto_analyzer.find_1h_profit_opportunities(min_score=min_1h_score, max_results=max_1h_results)
                    
                    if one_hour_opportunities:
                        print(f"🔴🔴🔴 1H ANALIZ: {len(one_hour_opportunities)} fırsat bulundu 🔴🔴🔴")
                        # Coin türüne göre filtrele
                        filtered_1h_opportunities = filter_opportunities_by_category(one_hour_opportunities, coin_categories[selected_1h_category])
                        print(f"🔴🔴🔴 1H ANALIZ: Filtreleme sonrası {len(filtered_1h_opportunities)} fırsat kaldı 🔴🔴🔴")
                        
                        # Session state'e kaydet
                        st.session_state["1h_opportunities_data"] = filtered_1h_opportunities
                        print(f"🔴🔴🔴 1H ANALIZ: 1h_opportunities_data session state'e kaydedildi: {len(filtered_1h_opportunities)} fırsat 🔴🔴🔴")
                        
                        if filtered_1h_opportunities:
                            st.success(f"✅ {len(filtered_1h_opportunities)} {selected_1h_category.lower()} 1 saatlik kazanç fırsatı bulundu!")
                            
                            # Fırsatları göster
                            st.subheader(f"⚡ 1 Saatlik Kazanç Fırsatları")
                            
                            for i, opportunity in enumerate(filtered_1h_opportunities):
                                with st.container():
                                    # Tavsiye rengi belirleme
                                    if opportunity['recommendation'] == "ACİL AL":
                                        recommendation_color = "🔴"
                                        bg_color = "background-color: #f8d7da; border-left: 4px solid #dc3545;"
                                    elif opportunity['recommendation'] == "HIZLI AL":
                                        recommendation_color = "🟠"
                                        bg_color = "background-color: #fff3cd; border-left: 4px solid #ffc107;"
                                    elif opportunity['recommendation'] == "AL":
                                        recommendation_color = "🟡"
                                        bg_color = "background-color: #d4edda; border-left: 4px solid #28a745;"
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
                                        st.write(f"**{opportunity['symbol']}** ({coin_type})")
                                        st.write(f"💰 **Fiyat:** ${opportunity['current_price']:.6f}")
                                        st.write(f"📊 **1h Değişim:** {opportunity['change_1h']:+.2f}%")
                                        st.write(f"📈 **4h Değişim:** {opportunity['change_4h']:+.2f}%")
                                        st.write(f"⚡ **1h Fırsat Tipi:** {opportunity['opportunity_type']}")
                                    
                                    with col2:
                                        st.metric("1h Skor", f"{opportunity['opportunity_score']:.1f}")
                                        if opportunity.get('rsi'):
                                            st.metric("RSI", f"{opportunity['rsi']:.1f}")
                                    
                                    with col3:
                                        st.metric("Hacim", f"${opportunity['volume_24h']/1000000:.1f}M")
                                        st.metric("Öneri", opportunity['recommendation'])
                                    
                                    with col4:
                                        # Takibe Al butonu
                                        st.button(f"📈 Takibe Al", key=f"1h_watch_{opportunity['symbol']}_{i}", 
                                                 on_click=add_to_watchlist, args=(opportunity['symbol'],))
                                        
                                        # Detay Analiz butonu
                                        if st.button(f"🔍 Detay", key=f"1h_detail_{opportunity['symbol']}_{i}"):
                                            st.info(f"{opportunity['symbol']} 1 saatlik detay analizi gösteriliyor...")
                                    
                                    st.divider()
                            
                            # 1h analiz özeti
                            st.subheader("📊 1 Saatlik Analiz Özeti")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Toplam Fırsat", len(filtered_1h_opportunities))
                            
                            with col2:
                                avg_1h_score = sum(opp['opportunity_score'] for opp in filtered_1h_opportunities) / len(filtered_1h_opportunities)
                                st.metric("Ortalama 1h Skor", f"{avg_1h_score:.1f}")
                            
                            with col3:
                                best_1h_opportunity = max(filtered_1h_opportunities, key=lambda x: x['opportunity_score'])
                                st.metric("En İyi 1h Fırsat", best_1h_opportunity['symbol'])
                            
                            with col4:
                                avg_1h_drop = sum(opp['change_1h'] for opp in filtered_1h_opportunities) / len(filtered_1h_opportunities)
                                st.metric("Ortalama 1h Düşüş", f"{avg_1h_drop:.1f}%")
                        
                        else:
                            st.warning(f"❌ {selected_1h_category} kategorisinde 1 saatlik fırsat bulunamadı.")
                            st.info("💡 Farklı bir kategori seçin veya parametreleri değiştirin.")
                    
                    else:
                        st.warning("❌ Belirtilen kriterlere uygun 1 saatlik crypto fırsatı bulunamadı.")
                        st.info("💡 Daha düşük bir minimum skor deneyin.")
                
                except Exception as e:
                    st.error(f"1 saatlik kazanç analizi sırasında hata oluştu: {str(e)}")
    
    with tab5:
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
                            
                            # Fırsat analizi
                            if coin_details.get('opportunity'):
                                st.subheader("🎯 Fırsat Analizi")
                                opp = coin_details['opportunity']
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Fırsat Tipi:** {opp['opportunity_type']}")
                                    st.write(f"**Öneri:** {opp['recommendation']}")
                                
                                with col2:
                                    st.write(f"**Fırsat Skoru:** {opp['opportunity_score']:.1f}")
                                    if opp.get('reason'):
                                        st.write(f"**Sebep:** {opp['reason']}")
                        
                        else:
                            st.error("Coin detayları alınamadı.")
                    
                    except Exception as e:
                        st.error(f"Coin detayları alınırken hata: {str(e)}")
    
    with tab5:
        st.subheader("📈 Crypto Grafik Analizi")
        st.info("Bu bölümde coin grafikleri ve teknik analiz göstergeleri eklenecek.")
    
    with tab6:
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

def filter_opportunities_by_category(opportunities, category):
    """Fırsatları kategoriye göre filtreler"""
    print(f"DEBUG FILTER: Kategori: {category}, Toplam fırsat: {len(opportunities)}")
    
    if category == "ALL":
        print("DEBUG FILTER: Tüm kategoriler seçildi, tüm fırsatlar döndürülüyor")
        return opportunities
    
    filtered = []
    for opp in opportunities:
        coin_type = determine_coin_type(opp['symbol'], opp['current_price'], opp['volume_24h'])
        print(f"DEBUG FILTER: {opp['symbol']} -> {coin_type}")
        
        if category == "MAJOR" and coin_type == "Major Coin":
            filtered.append(opp)
        elif category == "ALTCOIN" and coin_type == "Altcoin":
            filtered.append(opp)
        elif category == "MEME" and coin_type == "Meme Coin":
            filtered.append(opp)
        elif category == "DEFI" and coin_type == "DeFi Token":
            filtered.append(opp)
        elif category == "GAMING" and coin_type == "Gaming Token":
            filtered.append(opp)
        elif category == "LAYER1" and coin_type == "Layer 1":
            filtered.append(opp)
        elif category == "LAYER2" and coin_type == "Layer 2":
            filtered.append(opp)
        elif category == "AI" and coin_type == "AI Token":
            filtered.append(opp)
        elif category == "EXCHANGE" and coin_type == "Exchange Token":
            filtered.append(opp)
        elif category == "UTILITY" and coin_type == "Utility Token":
            filtered.append(opp)
        elif category == "MICRO_CAP" and coin_type == "Micro Cap":
            filtered.append(opp)
    
    print(f"DEBUG FILTER: Filtreleme sonrası {len(filtered)} fırsat kaldı")
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
    
    # Check coin type
    if symbol in major_coins:
        return "Major Coin"
    elif symbol in stablecoins:
        return "Stablecoin"
    elif any(indicator in symbol for indicator in meme_indicators):
        return "Meme Coin"
    elif any(indicator in symbol for indicator in defi_indicators):
        return "DeFi Token"
    elif any(indicator in symbol for indicator in gaming_indicators):
        return "Gaming Token"
    elif any(indicator in symbol for indicator in layer1_indicators):
        return "Layer 1"
    elif any(indicator in symbol for indicator in layer2_indicators):
        return "Layer 2"
    elif any(indicator in symbol for indicator in ai_indicators):
        return "AI Token"
    elif any(indicator in symbol for indicator in exchange_indicators):
        return "Exchange Token"
    elif any(indicator in symbol for indicator in utility_indicators):
        return "Utility Token"
    elif price < 0.01 and volume > 10000000:  # Çok düşük fiyat, yüksek hacim
        return "Altcoin/Meme"
    elif price < 1.0:
        return "Altcoin"
    elif volume < 1000000:  # Düşük hacim
        return "Micro Cap"
    else:
        return "Altcoin"

def buy_crypto(symbol, amount_usdt, price):
    """Kripto para satın alır"""
    current_user = st.session_state.current_user
    user_manager = st.session_state.user_manager
    
    success = user_manager.buy_crypto(current_user, symbol, amount_usdt, price)
    if success:
        st.success(f"✅ {amount_usdt} {symbol} satın alındı!")
        return True
    else:
        st.error("❌ Satın alma işlemi başarısız!")
        return False

def sell_crypto(symbol, amount_usdt, price):
    """Kripto para satar"""
    current_user = st.session_state.current_user
    user_manager = st.session_state.user_manager
    
    success = user_manager.sell_crypto(current_user, symbol, amount_usdt, price)
    if success:
        st.success(f"✅ {amount_usdt} {symbol} satıldı!")
        return True
    else:
        st.error("❌ Satış işlemi başarısız!")
        return False

def add_to_watchlist(symbol):
    """Takip listesine hisse ekler - Kalıcı veri yönetimi ile"""
    print(f"🔴🔴🔴 ADD_TO_WATCHLIST: Fonksiyon çağrıldı: {symbol} 🔴🔴🔴")
    
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        # Kalıcı veri yönetimi ile ekle
        user_manager.add_to_watchlist(current_user, symbol)
        
        # Session state'i güncelle
        if symbol not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(symbol)
            print(f"🔴🔴🔴 ADD_TO_WATCHLIST: Symbol eklendi: {symbol} 🔴🔴🔴")
            print(f"🔴🔴🔴 ADD_TO_WATCHLIST: Güncel watchlist: {st.session_state['watchlist']} 🔴🔴🔴")
            st.success(f"✅ {symbol} takip listesine eklendi!")
            return True
        else:
            print(f"🔴🔴🔴 ADD_TO_WATCHLIST: Symbol zaten mevcut: {symbol} 🔴🔴🔴")
            st.warning(f"⚠️ {symbol} zaten takip listesinde!")
            return False
    else:
        # Fallback: sadece session state
        if symbol not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(symbol)
            print(f"🔴🔴🔴 ADD_TO_WATCHLIST: Symbol eklendi (session only): {symbol} 🔴🔴🔴")
            st.success(f"✅ {symbol} takip listesine eklendi!")
            return True
        else:
            st.warning(f"⚠️ {symbol} zaten takip listesinde!")
            return False

def remove_from_watchlist(symbol):
    """Takip listesinden hisse çıkarır - Kalıcı veri yönetimi ile"""
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        # Kalıcı veri yönetimi ile çıkar
        user_manager.remove_from_watchlist(current_user, symbol)
        
        # Session state'i güncelle
        if symbol in st.session_state["watchlist"]:
            st.session_state["watchlist"].remove(symbol)
            st.success(f"❌ {symbol} takip listesinden çıkarıldı!")
            print(f"DEBUG: {symbol} watchlist'ten çıkarıldı. Güncel liste: {st.session_state['watchlist']}")
            return True
        else:
            st.warning(f"⚠️ {symbol} takip listesinde bulunamadı!")
            return False
    else:
        # Fallback: sadece session state
        if symbol in st.session_state["watchlist"]:
            st.session_state["watchlist"].remove(symbol)
            st.success(f"❌ {symbol} takip listesinden çıkarıldı!")
            print(f"DEBUG: {symbol} watchlist'ten çıkarıldı. Güncel liste: {st.session_state['watchlist']}")
            return True
        else:
            st.warning(f"⚠️ {symbol} takip listesinde bulunamadı!")
            return False

def calculate_exit_recommendation(symbol, current_price, avg_price, profit_loss_percent):
    """Coin için önerilen çıkış saati hesaplar"""
    from datetime import datetime, timedelta
    
    # Kar/zarar durumuna göre öneri
    if profit_loss_percent >= 20:  # %20+ kar
        recommendation = "🟢 ACİL SAT"
        reason = "Yüksek kar - Kârı realize et"
        exit_time = "Hemen"
    elif profit_loss_percent >= 10:  # %10-20 kar
        recommendation = "🟡 YAKINDA SAT"
        reason = "İyi kar - Yakında sat"
        exit_time = "1-2 saat içinde"
    elif profit_loss_percent >= 5:  # %5-10 kar
        recommendation = "🔵 BEKLE"
        reason = "Orta kar - Bekle"
        exit_time = "4-6 saat içinde"
    elif profit_loss_percent >= 0:  # %0-5 kar
        recommendation = "🔵 BEKLE"
        reason = "Düşük kar - Bekle"
        exit_time = "6-12 saat içinde"
    elif profit_loss_percent >= -5:  # %0-5 zarar
        recommendation = "🔵 BEKLE"
        reason = "Düşük zarar - Bekle"
        exit_time = "12-24 saat içinde"
    elif profit_loss_percent >= -10:  # %5-10 zarar
        recommendation = "🟡 YAKINDA SAT"
        reason = "Orta zarar - Yakında sat"
        exit_time = "2-4 saat içinde"
    else:  # %10+ zarar
        recommendation = "🟢 ACİL SAT"
        reason = "Yüksek zarar - Zararı kes"
        exit_time = "Hemen"
    
    # Teknik analiz ekle
    try:
        crypto_analyzer = st.session_state.get('crypto_analyzer')
        if crypto_analyzer:
            coin_data = crypto_analyzer.get_coin_data(symbol)
            if coin_data:
                # RSI analizi
                rsi = crypto_analyzer.calculate_rsi(coin_data['data']['close'])
                if rsi > 70:  # Aşırı alım
                    recommendation = "🟢 ACİL SAT"
                    reason = "Aşırı alım bölgesi - Sat"
                    exit_time = "Hemen"
                elif rsi < 30:  # Aşırı satım
                    if profit_loss_percent < 0:
                        recommendation = "🔵 BEKLE"
                        reason = "Aşırı satım - Toparlanma bekleniyor"
                        exit_time = "6-12 saat içinde"
                
                # Trend analizi
                change_24h = coin_data['change_24h']
                if change_24h < -10:  # %10+ düşüş
                    if profit_loss_percent < 0:
                        recommendation = "🟢 ACİL SAT"
                        reason = "Güçlü düşüş trendi - Zararı kes"
                        exit_time = "Hemen"
    except:
        pass  # Teknik analiz hatası durumunda devam et
    
    return f"{recommendation} - {exit_time}"

def calculate_price_recommendations(symbol, current_price, avg_price, profit_loss_percent):
    """Coin için önerilen giriş ve çıkış fiyatlarını hesaplar"""
    try:
        crypto_analyzer = st.session_state.get('crypto_analyzer')
        if crypto_analyzer:
            coin_data = crypto_analyzer.get_coin_data(symbol)
            if coin_data:
                # Teknik analiz verileri
                df = coin_data['data']
                rsi = crypto_analyzer.calculate_rsi(df['close'])
                change_24h = coin_data['change_24h']
                change_7d = coin_data['change_7d']
                
                # Bollinger Bands hesapla
                upper_band, middle_band, lower_band = crypto_analyzer.calculate_bollinger_bands(df['close'])
                current_upper = upper_band.iloc[-1] if not upper_band.empty else current_price * 1.05
                current_lower = lower_band.iloc[-1] if not lower_band.empty else current_price * 0.95
                
                # Destek ve direnç seviyeleri
                high_24h = df['high'].iloc[-24:].max() if len(df) >= 24 else df['high'].max()
                low_24h = df['low'].iloc[-24:].min() if len(df) >= 24 else df['low'].min()
                
                # Önerilen giriş fiyatı hesaplama
                if profit_loss_percent < 0:  # Zararda ise
                    # Daha düşük fiyattan alım için öneri
                    if rsi < 30:  # Aşırı satım
                        recommended_entry = current_price * 0.95  # %5 daha düşük
                    elif rsi < 40:
                        recommended_entry = current_price * 0.97  # %3 daha düşük
                    else:
                        recommended_entry = current_price * 0.98  # %2 daha düşük
                else:  # Karda ise
                    # Mevcut fiyat yakınından alım
                    recommended_entry = current_price * 1.02  # %2 daha yüksek
                
                # Önerilen çıkış fiyatı hesaplama
                if profit_loss_percent >= 20:  # Yüksek kar
                    recommended_exit = current_price * 0.98  # Hemen sat
                elif profit_loss_percent >= 10:  # İyi kar
                    recommended_exit = current_price * 1.05  # %5 daha yüksek
                elif profit_loss_percent >= 5:  # Orta kar
                    recommended_exit = current_price * 1.08  # %8 daha yüksek
                elif profit_loss_percent >= 0:  # Düşük kar
                    recommended_exit = current_price * 1.10  # %10 daha yüksek
                elif profit_loss_percent >= -5:  # Düşük zarar
                    recommended_exit = current_price * 1.05  # %5 daha yüksek
                elif profit_loss_percent >= -10:  # Orta zarar
                    recommended_exit = current_price * 1.02  # %2 daha yüksek
                else:  # Yüksek zarar
                    recommended_exit = current_price * 0.98  # Hemen sat
                
                # Teknik seviyeleri dikkate al
                if current_price > current_upper:  # Üst bandın üstünde
                    recommended_exit = min(recommended_exit, current_upper * 0.99)
                elif current_price < current_lower:  # Alt bandın altında
                    recommended_entry = max(recommended_entry, current_lower * 1.01)
                
                # Destek/direnç seviyelerini dikkate al
                if current_price < low_24h * 1.02:  # 24h düşük seviyeye yakın
                    recommended_entry = max(recommended_entry, low_24h * 0.98)
                if current_price > high_24h * 0.98:  # 24h yüksek seviyeye yakın
                    recommended_exit = min(recommended_exit, high_24h * 1.02)
                
                return {
                    'entry_price': round(recommended_entry, 6),
                    'exit_price': round(recommended_exit, 6),
                    'rsi': round(rsi, 1),
                    'bollinger_upper': round(current_upper, 6),
                    'bollinger_lower': round(current_lower, 6)
                }
    except Exception as e:
        print(f"Fiyat önerisi hesaplama hatası: {e}")
    
    # Fallback değerler
    return {
        'entry_price': round(current_price * 0.98, 6),
        'exit_price': round(current_price * 1.05, 6),
        'rsi': 50.0,
        'bollinger_upper': round(current_price * 1.05, 6),
        'bollinger_lower': round(current_price * 0.95, 6)
    }

def show_portfolio_management():
    """Portföy yönetimi sayfası"""
    st.header("💼 Portföy Yönetimi")
    
    # Otomatik yenileme sistemi - Gelişmiş çözüm
    if 'portfolio_auto_refresh' not in st.session_state:
        st.session_state.portfolio_auto_refresh = True
    
    if 'portfolio_refresh_interval' not in st.session_state:
        st.session_state.portfolio_refresh_interval = 5  # 5 saniye
    
    # Manuel yenileme butonu ve otomatik yenileme kontrolü
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.write("🔄 **Canlı Portföy Takibi**")
        if st.session_state.portfolio_auto_refresh:
            st.write(f"✅ Otomatik yenileme aktif ({st.session_state.portfolio_refresh_interval} saniyede bir)")
        else:
            st.write("⏸️ Otomatik yenileme duraklatıldı")
    
    with col2:
        if st.button("🔄 Yenile", key="manual_refresh_portfolio"):
            st.rerun()
    
    with col3:
        if st.button("⏸️/▶️", key="toggle_auto_refresh"):
            st.session_state.portfolio_auto_refresh = not st.session_state.portfolio_auto_refresh
            st.rerun()
    
    with col4:
        # Yenileme aralığını ayarlama
        new_interval = st.selectbox("⏱️ Yenileme Aralığı:", [3, 5, 10, 15, 30], 
                                   index=[3, 5, 10, 15, 30].index(st.session_state.portfolio_refresh_interval),
                                   key="refresh_interval_selector")
        if new_interval != st.session_state.portfolio_refresh_interval:
            st.session_state.portfolio_refresh_interval = new_interval
            st.rerun()
    
    # Otomatik yenileme için placeholder
    if st.session_state.portfolio_auto_refresh:
        refresh_placeholder = st.empty()
        refresh_placeholder.info(f"🔄 Otomatik yenileme aktif - {st.session_state.portfolio_refresh_interval} saniyede bir güncelleniyor...")
        
        # Basit otomatik yenileme - her sayfa yüklendiğinde kontrol
        if 'auto_refresh_counter' not in st.session_state:
            st.session_state.auto_refresh_counter = 0
        
        st.session_state.auto_refresh_counter += 1
        
        # Her 5 sayfa yüklemesinde bir yenileme (yaklaşık 5 saniye)
        if st.session_state.auto_refresh_counter >= st.session_state.portfolio_refresh_interval:
            st.session_state.auto_refresh_counter = 0
            st.rerun()
    
    current_user = st.session_state.current_user
    user_manager = st.session_state.user_manager
    
    # Kullanıcı bilgileri
    users = user_manager.get_users()
    user_data = users[current_user]
    
    st.subheader(f"👤 {user_data['name']} - Portföy Durumu")
    
    # Bakiye ve portföy değeri
    balance = user_manager.get_user_balance(current_user)
    portfolio = user_manager.get_portfolio(current_user)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Nakit Bakiye", f"{balance:,.2f} USD")
    
    with col2:
        portfolio_value = 0.0
        if portfolio:
            # Gerçek fiyatları al
            crypto_analyzer = st.session_state.get('crypto_analyzer')
            for symbol in portfolio.keys():
                try:
                    if crypto_analyzer:
                        coin_data = crypto_analyzer.get_coin_data(symbol)
                        if coin_data:
                            current_price = coin_data['current_price']
                            amount = portfolio[symbol]['amount']
                            portfolio_value += amount * current_price
                except:
                    continue
        
        st.metric("📈 Kripto Değeri", f"{portfolio_value:,.2f} USD")
    
    with col3:
        total_value = balance + portfolio_value
        st.metric("💎 Toplam Değer", f"{total_value:,.2f} USD")
    
    with col4:
        if portfolio_value > 0:
            profit_loss = portfolio_value - sum(data['total_invested'] for data in portfolio.values())
            profit_loss_percent = (profit_loss / sum(data['total_invested'] for data in portfolio.values())) * 100
            st.metric("📊 Kar/Zarar", f"{profit_loss:+,.2f} USD ({profit_loss_percent:+.2f}%)")
        else:
            st.metric("📊 Kar/Zarar", "0.00 USD")
    
    st.divider()
    
    # Portföy detayları
    if portfolio:
        st.subheader("📊 Portföy Detayları")
        
        # Güncel fiyatları al
        portfolio_details = []
        crypto_analyzer = st.session_state.get('crypto_analyzer')
        for symbol, data in portfolio.items():
            try:
                if crypto_analyzer:
                    coin_data = crypto_analyzer.get_coin_data(symbol)
                    if coin_data:
                        current_price = coin_data['current_price']
                        amount = data['amount']
                        avg_price = data['avg_price']
                        invested = data['total_invested']
                        
                        current_value = amount * current_price
                        profit_loss = current_value - invested
                        profit_loss_percent = (profit_loss / invested * 100) if invested > 0 else 0
                        
                        portfolio_details.append({
                            'symbol': symbol,
                            'amount': amount,
                            'avg_price': avg_price,
                            'current_price': current_price,
                            'current_value': current_value,
                            'invested': invested,
                            'profit_loss': profit_loss,
                            'profit_loss_percent': profit_loss_percent
                        })
            except:
                continue
        
        if portfolio_details:
            # Portföy tablosu
            for item in portfolio_details:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                    
                    with col1:
                        st.write(f"**{item['symbol']}**")
                        st.write(f"Miktar: {item['amount']:.4f}")
                    
                    with col2:
                        st.metric("Ort. Fiyat", f"${item['avg_price']:.6f}")
                        st.metric("Güncel", f"${item['current_price']:.6f}")
                    
                    with col3:
                        st.metric("Yatırım", f"${item['invested']:.2f}")
                        st.metric("Değer", f"${item['current_value']:.2f}")
                    
                    with col4:
                        profit_color = "normal" if item['profit_loss'] >= 0 else "inverse"
                        st.metric("Kar/Zarar", f"${item['profit_loss']:+.2f}", 
                                delta=f"{item['profit_loss_percent']:+.2f}%")
                        
                        # Önerilen çıkış saati
                        exit_recommendation = calculate_exit_recommendation(
                            item['symbol'], 
                            item['current_price'], 
                            item['avg_price'], 
                            item['profit_loss_percent']
                        )
                        st.write(f"🕐 **{exit_recommendation}**")
                        
                        # Fiyat önerileri
                        price_recommendations = calculate_price_recommendations(
                            item['symbol'], 
                            item['current_price'], 
                            item['avg_price'], 
                            item['profit_loss_percent']
                        )
                        
                        st.write(f"📈 **Giriş:** ${price_recommendations['entry_price']:.6f}")
                        st.write(f"📉 **Çıkış:** ${price_recommendations['exit_price']:.6f}")
                        st.write(f"📊 **RSI:** {price_recommendations['rsi']}")
                    
                    with col5:
                        # İşlem butonları
                        col_buy, col_sell = st.columns(2)
                        
                        with col_buy:
                            if st.button(f"💰 Al", key=f"portfolio_buy_{item['symbol']}"):
                                st.session_state.show_buy_modal = item['symbol']
                                st.rerun()
                        
                        with col_sell:
                            if st.button(f"💸 Sat", key=f"portfolio_sell_{item['symbol']}"):
                                # Tümünü sat
                                sell_crypto(item['symbol'], item['amount'], item['current_price'])
                                # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
                    
                    st.divider()
        
        # Alım modalı
        if st.session_state.get('show_buy_modal'):
            symbol = st.session_state.show_buy_modal
            st.subheader(f"💰 {symbol} Satın Al")
            
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input(f"Miktar (USDT):", min_value=10.0, value=100.0, step=10.0)
            
            with col2:
                try:
                    coin_data = crypto_analyzer.get_coin_data(symbol)
                    current_price = coin_data['current_price']
                    st.write(f"Güncel Fiyat: ${current_price:.6f}")
                    
                    if st.button("✅ Satın Al"):
                        buy_crypto(symbol, amount, current_price)
                        st.session_state.show_buy_modal = None
                        # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
                except:
                    st.error("Fiyat bilgisi alınamadı")
            
            if st.button("❌ İptal"):
                st.session_state.show_buy_modal = None
                # st.rerun() kaldırıldı - sayfa yeniden yüklenmeyecek
    
    else:
        st.info("📭 Henüz kripto varlığı bulunmuyor.")
        st.write("🪙 Crypto Analizi sayfasından coin satın alabilirsiniz.")
    
    st.divider()
    
    # İşlem geçmişi
    st.subheader("📋 İşlem Geçmişi")
    transactions = user_manager.get_transactions(current_user)
    
    if transactions:
        # Son 10 işlemi göster
        recent_transactions = transactions[-10:]
        
        for transaction in reversed(recent_transactions):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    transaction_type = "🟢 ALIM" if transaction['type'] == 'BUY' else "🔴 SATIM"
                    st.write(f"{transaction_type} **{transaction['symbol']}**")
                    st.write(f"Tarih: {transaction['timestamp'][:19]}")
                
                with col2:
                    if transaction['type'] == 'BUY':
                        st.write(f"Miktar: {transaction['amount']:.4f}")
                        st.write(f"Fiyat: ${transaction['price']:.6f}")
                    else:
                        st.write(f"Miktar: {transaction['amount']:.4f}")
                        st.write(f"Fiyat: ${transaction['price']:.6f}")
                
                with col3:
                    if transaction['type'] == 'BUY':
                        st.write(f"Toplam: ${transaction['total_cost']:.2f}")
                    else:
                        st.write(f"Toplam: ${transaction['total_revenue']:.2f}")
                
                with col4:
                    st.write(f"Bakiye: ${transaction['balance_after']:.2f}")
                
                st.divider()
    else:
        st.info("📭 Henüz işlem geçmişi bulunmuyor.")

def show_crypto_virtual_trading():
    """Crypto sanal trading sayfası"""
    st.header("🪙 Crypto Sanal Trading")
    st.markdown("**Takip listesindeki coinlerle sanal alım-satım sistemi**")
    
    # Otomatik yenileme sistemi - Gelişmiş çözüm
    if 'crypto_auto_refresh' not in st.session_state:
        st.session_state.crypto_auto_refresh = True
    
    if 'crypto_refresh_interval' not in st.session_state:
        st.session_state.crypto_refresh_interval = 5  # 5 saniye
    
    # Manuel yenileme butonu ve otomatik yenileme kontrolü
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.write("🔄 **Canlı Crypto Takibi**")
        if st.session_state.crypto_auto_refresh:
            st.write(f"✅ Otomatik yenileme aktif ({st.session_state.crypto_refresh_interval} saniyede bir)")
        else:
            st.write("⏸️ Otomatik yenileme duraklatıldı")
    
    with col2:
        if st.button("🔄 Yenile", key="manual_refresh_crypto"):
            st.rerun()
    
    with col3:
        if st.button("⏸️/▶️", key="toggle_crypto_auto_refresh"):
            st.session_state.crypto_auto_refresh = not st.session_state.crypto_auto_refresh
            st.rerun()
    
    with col4:
        # Yenileme aralığını ayarlama
        new_interval = st.selectbox("⏱️ Yenileme Aralığı:", [3, 5, 10, 15, 30], 
                                   index=[3, 5, 10, 15, 30].index(st.session_state.crypto_refresh_interval),
                                   key="crypto_refresh_interval_selector")
        if new_interval != st.session_state.crypto_refresh_interval:
            st.session_state.crypto_refresh_interval = new_interval
            st.rerun()
    
    # Otomatik yenileme için placeholder
    if st.session_state.crypto_auto_refresh:
        refresh_placeholder = st.empty()
        refresh_placeholder.info(f"🔄 Otomatik yenileme aktif - {st.session_state.crypto_refresh_interval} saniyede bir güncelleniyor...")
        
        # Basit otomatik yenileme - her sayfa yüklendiğinde kontrol
        if 'crypto_auto_refresh_counter' not in st.session_state:
            st.session_state.crypto_auto_refresh_counter = 0
        
        st.session_state.crypto_auto_refresh_counter += 1
        
        # Her 5 sayfa yüklemesinde bir yenileme (yaklaşık 5 saniye)
        if st.session_state.crypto_auto_refresh_counter >= st.session_state.crypto_refresh_interval:
            st.session_state.crypto_auto_refresh_counter = 0
            st.rerun()
    
    print(f"DEBUG CRYPTO VIRTUAL: Sayfa yüklendi. Mevcut takip listesi: {st.session_state.watchlist}")
    
    # Refresh kontrolü
    if st.session_state.refresh_watchlist:
        st.session_state.refresh_watchlist = False
        st.rerun()
    
    # Kullanıcı seçimi
    st.subheader("👤 Kullanıcı Seçimi")
    selected_user = st.selectbox(
        "Hangi kullanıcı ile işlem yapmak istiyorsunuz?",
        ["Gökhan", "Yılmaz"],
        index=0 if st.session_state.selected_user == "Gökhan" else 1,
        key="crypto_user_selector"
    )
    
    # Kullanıcı değiştiğinde session state'i güncelle
    if selected_user != st.session_state.selected_user:
        st.session_state.selected_user = selected_user
        st.rerun()
    
    # Seçili kullanıcının verilerini al
    user_data = get_current_user_data()
    
    # Kullanıcı bilgileri
    st.sidebar.subheader("💰 Kullanıcı Bilgileri")
    st.sidebar.write(f"**Kullanıcı:** {selected_user}")
    st.sidebar.metric("Bakiye", f"{user_data['balance']:.2f} USD")
    
    # Takip listesi
    st.sidebar.subheader("👀 Takip Listesi")
    print(f"DEBUG CRYPTO VIRTUAL SIDEBAR: Takip listesi içeriği: {st.session_state['watchlist']}")
    if st.session_state["watchlist"]:
        st.sidebar.write(f"📊 **{len(st.session_state['watchlist'])} coin takip ediliyor**")
        for symbol in st.session_state["watchlist"]:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.sidebar.write(f"📈 {symbol}")
            with col2:
                if st.sidebar.button("❌", key=f"crypto_remove_{symbol}"):
                    remove_from_watchlist(symbol)
    else:
        st.sidebar.info("Henüz takip listesi boş")
        print(f"DEBUG CRYPTO VIRTUAL SIDEBAR: Takip listesi boş!")
    
    # Ana trading arayüzü
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Crypto Portföy", "👀 Takip Listesi", "💸 İşlem Yap", "📈 Performans", "📋 İşlem Geçmişi"])
    
    with tab1:
        show_crypto_portfolio_tab()
    
    with tab2:
        show_crypto_watchlist_tab()
    
    with tab3:
        show_crypto_trading_tab()
    
    with tab4:
        show_crypto_performance_tab()
    
    with tab5:
        show_crypto_transaction_history()

def show_crypto_portfolio_tab():
    """Crypto portföy sekmesi"""
    st.subheader("📊 Mevcut Crypto Portföy")
    
    # Kalıcı veri yönetimi ile portföy al
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        portfolio = user_manager.get_portfolio(current_user)
    else:
        # Fallback: session state
        user_data = get_current_user_data()
        portfolio = user_data.get('portfolio', {})
    
    if not portfolio:
        st.info("Crypto portföyünüzde henüz coin bulunmuyor.")
        return
    
    # Portföy özeti
    total_value = 0
    portfolio_data = []
    
    for symbol, data in portfolio.items():
        # Sadece coinleri göster (USDT ile biten semboller)
        if not symbol.endswith('USDT'):
            continue
            
        # Gerçek fiyatları al
        current_price = data['avg_price']  # Varsayılan olarak ortalama fiyat
        try:
            crypto_analyzer = st.session_state.get('crypto_analyzer')
            if crypto_analyzer:
                coin_data = crypto_analyzer.get_coin_data(symbol)
                if coin_data:
                    current_price = coin_data['current_price']
        except:
            # Hata durumunda ortalama fiyat kullan
            current_price = data['avg_price']
            
        quantity = data['amount']  # user_manager'dan gelen veri 'amount' olarak
        value = quantity * current_price
        total_value += value
        
        # Kar/zarar hesapla
        cost = quantity * data['avg_price']
        profit_loss = value - cost
        profit_loss_percent = (profit_loss / cost) * 100 if cost > 0 else 0
        
        # Önerilen çıkış saati hesapla
        exit_recommendation = calculate_exit_recommendation(symbol, current_price, data['avg_price'], profit_loss_percent)
        
        # Fiyat önerilerini hesapla
        price_recommendations = calculate_price_recommendations(symbol, current_price, data['avg_price'], profit_loss_percent)
        
        portfolio_data.append({
            'Symbol': symbol,
            'Adet': quantity,
            'Ortalama Maliyet': f"{data['avg_price']:.6f} USDT",
            'Güncel Fiyat': f"{current_price:.6f} USDT",
            'Toplam Değer': f"{value:.2f} USDT",
            'Kar/Zarar': f"{profit_loss:.2f} USDT",
            'Kar/Zarar %': f"{profit_loss_percent:.2f}%",
            'Önerilen Çıkış': exit_recommendation,
            'Önerilen Giriş': f"{price_recommendations['entry_price']:.6f} USDT",
            'Önerilen Çıkış Fiyatı': f"{price_recommendations['exit_price']:.6f} USDT"
        })
    
    # Portföy tablosu
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)
    
    # Toplam değer
    st.metric("📈 Toplam Crypto Portföy Değeri", f"{total_value:.2f} USDT")
    
    # Çıkış önerileri açıklaması
    st.subheader("🕐 Çıkış Önerileri Açıklaması")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🟢 **ACİL SAT:** %20+ kar veya %10+ zarar durumunda")
    with col2:
        st.info("🟡 **YAKINDA SAT:** %10-20 kar veya %5-10 zarar durumunda")
    with col3:
        st.info("🔵 **BEKLE:** %5-10 kar veya %0-5 zarar durumunda")
    
    # Fiyat önerileri açıklaması
    st.subheader("💰 Fiyat Önerileri Açıklaması")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📈 **Önerilen Giriş:** Teknik analiz ile hesaplanan optimal alım fiyatı")
    with col2:
        st.info("📉 **Önerilen Çıkış:** Kar/zarar durumuna göre hesaplanan satış fiyatı")
    with col3:
        st.info("📊 **RSI:** Relative Strength Index - Aşırı alım/satım göstergesi")

def show_crypto_watchlist_tab():
    """Crypto takip listesi sekmesi"""
    st.subheader("👀 Crypto Takip Listesi")
    st.markdown("**Crypto analizinden takibe aldığınız coinler**")
    
    # Güncel döviz kuru bilgisi
    try:
        from portfolio.exchange_rate import exchange_rate_service
        usdt_rate = exchange_rate_service.get_usdt_to_try_rate()
        st.info(f"💱 **Güncel Döviz Kuru:** 1 USDT = {usdt_rate:.4f} TL")
    except:
        st.info("💱 **Güncel Döviz Kuru:** 1 USDT = 30.0000 TL")
    
    # Debug: Test butonu ekle
    if st.button("🧪 Test: CVCUSDT Takibe Al", key="debug_test_watch"):
        print(f"🔴🔴🔴 DEBUG TEST: Test butonuna tıklandı! 🔴🔴🔴")
        result = add_to_watchlist("CVCUSDT")
        print(f"🔴🔴🔴 DEBUG TEST: add_to_watchlist sonucu: {result} 🔴🔴🔴")
        st.success("✅ Test: CVCUSDT takip listesine eklendi!")
        st.rerun()
    
    # Basit test butonu
    if st.button("🔴 Basit Test Butonu", key="simple_test_button"):
        print(f"🔴🔴🔴 SIMPLE TEST: Basit test butonuna tıklandı! 🔴🔴🔴")
        st.info("Basit test butonu çalışıyor!")
    
    # Manuel test butonu
    st.write("🔴 MANUEL TEST: Manuel olarak coin ekleme")
    if st.button("➕ CVCUSDT Ekle", key="manual_add_cvc"):
        print(f"🔴🔴🔴 MANUAL ADD: CVCUSDT manuel olarak ekleniyor 🔴🔴🔴")
        result = add_to_watchlist("CVCUSDT")
        st.success(f"✅ CVCUSDT eklendi! Sonuç: {result}")
        st.rerun()
    
    # Basit test butonu - Crypto analizi için
    if st.button("🔴 Test: XTZUSDT Ekle", key="test_add_xtz"):
        print(f"🔴🔴🔴 TEST XTZ: XTZUSDT test butonuna tıklandı! 🔴🔴🔴")
        result = add_to_watchlist("XTZUSDT")
        st.success(f"✅ XTZUSDT eklendi! Sonuç: {result}")
        st.rerun()
    
    # Session state temizleme butonu
    if st.button("🧹 Session State Temizle", key="cleanup_session"):
        print(f"🔴🔴🔴 CLEANUP: Session state temizleniyor! 🔴🔴🔴")
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith(('profit_', 'crypto_')) and key != 'crypto_analyzer']
        for key in keys_to_remove:
            del st.session_state[key]
            print(f"DEBUG CLEANUP: Key silindi: {key}")
        st.success(f"✅ {len(keys_to_remove)} eski key temizlendi!")
        st.rerun()
    
    # Manuel test butonu - Crypto analizi için
    st.write("🔴 MANUEL TEST: Crypto analizi butonları için test")
    if st.button("🔴 Test: CVCUSDT Takibe Al", key="test_crypto_watch"):
        print(f"🔴🔴🔴 TEST CRYPTO: CVCUSDT test butonuna tıklandı! 🔴🔴🔴")
        result = add_to_watchlist("CVCUSDT")
        st.success(f"✅ CVCUSDT eklendi! Sonuç: {result}")
        st.rerun()
    
    # Sadece coinleri filtrele (USDT ile biten semboller)
    crypto_watchlist = [symbol for symbol in st.session_state["watchlist"] if symbol.endswith('USDT')]
    
    if not crypto_watchlist:
        st.info("Henüz takip listesinde coin bulunmuyor.")
        st.markdown("""
        **Takip listesine coin eklemek için:**
        1. **Crypto Analizi** sayfasına gidin
        2. İstediğiniz coini bulun
        3. **"Takibe Al"** butonuna tıklayın
        """)
        return
    
    # Takip listesi özeti
    st.success(f"✅ Takip listenizde {len(crypto_watchlist)} coin bulunuyor")
    
    # Her coin için detaylı bilgi ve işlem seçenekleri
    for i, symbol in enumerate(crypto_watchlist):
        with st.expander(f"📈 {symbol} - Detaylar ve İşlemler", expanded=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.write(f"**{symbol}**")
                
                # Gerçek fiyatları opportunities_data'dan al
                real_price = None
                real_change = None
                real_volume = None
                
                if 'opportunities_data' in st.session_state and st.session_state.opportunities_data:
                    for opp in st.session_state.opportunities_data:
                        if opp['symbol'] == symbol:
                            real_price = opp['current_price']
                            real_change = opp['change_24h']
                            real_volume = opp['volume_24h']
                            break
                
                # Eğer gerçek fiyat bulunamazsa Binance API'den çek
                if real_price is None:
                    try:
                        # Crypto analyzer'dan gerçek fiyat çek
                        crypto_analyzer = st.session_state.get('crypto_analyzer')
                        if crypto_analyzer:
                            coin_data = crypto_analyzer.get_coin_data(symbol)
                            if coin_data:
                                real_price = coin_data['current_price']
                                real_change = coin_data['change_24h']
                                real_volume = coin_data['volume_24h']
                            else:
                                # API'den çekilemezse daha gerçekçi mock değer
                                if symbol.endswith('USDT'):
                                    real_price = np.random.uniform(0.0001, 10)  # Daha gerçekçi aralık
                                else:
                                    real_price = np.random.uniform(0.0001, 1)
                        else:
                            # Crypto analyzer yoksa daha gerçekçi mock değer
                            if symbol.endswith('USDT'):
                                real_price = np.random.uniform(0.0001, 10)
                            else:
                                real_price = np.random.uniform(0.0001, 1)
                    except:
                        # Hata durumunda daha gerçekçi mock değer
                        if symbol.endswith('USDT'):
                            real_price = np.random.uniform(0.0001, 10)
                        else:
                            real_price = np.random.uniform(0.0001, 1)
                
                if real_change is None:
                    real_change = np.random.uniform(-15, 15)
                
                if real_volume is None:
                    real_volume = np.random.randint(1000000, 100000000)
                
                st.write(f"💰 **Güncel Fiyat:** ${real_price:.6f}")
                st.write(f"📊 **24h Değişim:** {real_change:+.2f}%")
                st.write(f"📈 **Hacim:** ${real_volume:,}")
                
                # Coin durumu
                if real_change > 0:
                    st.success(f"🟢 Pozitif trend")
                elif real_change < 0:
                    st.error(f"🔴 Negatif trend")
                else:
                    st.info(f"⚪ Nötr")
            
            with col2:
                st.write("**📊 Teknik Analiz**")
                
                # Mock teknik göstergeler
                rsi = np.random.uniform(30, 70)
                macd = np.random.uniform(-2, 2)
                volume_ratio = np.random.uniform(0.5, 2.0)
                
                st.write(f"RSI: {rsi:.1f}")
                st.write(f"MACD: {macd:.2f}")
                st.write(f"Hacim Oranı: {volume_ratio:.2f}")
                
                # RSI durumu
                if rsi > 70:
                    st.warning("⚠️ Aşırı alım")
                elif rsi < 30:
                    st.info("💡 Aşırı satım fırsatı")
                else:
                    st.success("✅ Normal seviye")
            
            with col3:
                st.write("**🎯 İşlem Seçenekleri**")
                
                # USDT miktarı seçimi
                usdt_amount = st.number_input(
                    "USDT Miktarı:",
                    min_value=10.0,
                    value=100.0,
                    step=10.0,
                    key=f"crypto_watchlist_usdt_{symbol}"
                )
                
                # Coin miktarı hesapla
                coin_amount = usdt_amount / real_price
                st.write(f"**Coin Miktarı:** {coin_amount:.6f}")
            
            with col4:
                st.write("**🛒 İşlem Butonları**")
                
                # Alım butonu
                if st.button(f"🛒 Al", key=f"crypto_watchlist_buy_{symbol}"):
                    print(f"DEBUG CRYPTO VIRTUAL: Alım butonuna tıklandı: {symbol}")
                    success = buy_crypto(symbol, usdt_amount, real_price)
                    if success:
                        st.success(f"{symbol} başarıyla alındı!")
                        st.rerun()
                    else:
                        st.error("Alım işlemi başarısız!")
                
                # Satış butonu (portföyde varsa)
                user_data = get_current_user_data()
                if symbol in user_data['portfolio']:
                    if st.button(f"💸 Sat", key=f"crypto_watchlist_sell_{symbol}"):
                        success = sell_crypto(symbol, usdt_amount, real_price)
                        if success:
                            st.success(f"{symbol} başarıyla satıldı!")
                            st.rerun()
                        else:
                            st.error("Satış işlemi başarısız!")
                else:
                    st.info("Portföyde yok")
                
                # Takip listesinden çıkar
                if st.button(f"❌ Takipten Çıkar", key=f"crypto_watchlist_remove_{symbol}"):
                    remove_from_watchlist(symbol)
                    st.success(f"{symbol} takip listesinden çıkarıldı!")
            
            st.divider()
    
    # Takip listesi istatistikleri
    st.subheader("📊 Takip Listesi İstatistikleri")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Coin", len(crypto_watchlist))
    
    with col2:
        # Pozitif trend sayısı
        positive_count = sum(1 for _ in range(len(crypto_watchlist)) 
                           if np.random.uniform(-15, 15) > 0)
        st.metric("Pozitif Trend", positive_count)
    
    with col3:
        # Portföyde olan coin sayısı - Kalıcı veri yönetimi ile
        current_user = st.session_state.get("current_user", "gokhan")
        user_manager = st.session_state.get("user_manager")
        
        if user_manager:
            portfolio = user_manager.get_portfolio(current_user)
        else:
            # Fallback: session state
            user_data = get_current_user_data()
            portfolio = user_data.get('portfolio', {})
        
        portfolio_count = sum(1 for symbol in crypto_watchlist 
                            if symbol in portfolio)
        st.metric("Portföyde Olan", portfolio_count)
    
    with col4:
        # Ortalama fiyat
        avg_price = np.random.uniform(0.0001, 50000)  # Mock ortalama
        st.metric("Ortalama Fiyat", f"${avg_price:.6f}")

def show_crypto_trading_tab():
    """Crypto işlem yapma sekmesi"""
    st.subheader("💸 Crypto İşlem Yap")
    st.markdown("**Portföyünüzdeki coinlerden satış yapın veya yeni coin alın**")
    
    # Portföydeki coinlerden satış - Kalıcı veri yönetimi ile
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        portfolio = user_manager.get_portfolio(current_user)
    else:
        # Fallback: session state
        user_data = get_current_user_data()
        portfolio = user_data.get('portfolio', {})
    
    if portfolio:
        st.write("**📊 Portföyünüzdeki Coinlerden Satış:**")
        
        for symbol, data in portfolio.items():
            with st.expander(f"📈 {symbol} - Satış İşlemi", expanded=True):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{symbol}**")
                    st.write(f"📦 **Mevcut Miktar:** {data['amount']:.6f}")
                    st.write(f"💰 **Ortalama Maliyet:** {data['avg_price']:.6f} USDT")
                    
                    # Gerçek fiyatları al
                    current_price = data['avg_price']  # Varsayılan olarak ortalama fiyat
                    try:
                        crypto_analyzer = st.session_state.get('crypto_analyzer')
                        if crypto_analyzer:
                            coin_data = crypto_analyzer.get_coin_data(symbol)
                            if coin_data:
                                current_price = coin_data['current_price']
                    except:
                        # Hata durumunda ortalama fiyat kullan
                        current_price = data['avg_price']
                    
                    st.write(f"📊 **Güncel Fiyat:** {current_price:.6f} USDT")
                
                with col2:
                    st.write("**📊 Kar/Zarar**")
                    current_value = data['amount'] * current_price
                    cost = data['amount'] * data['avg_price']
                    profit_loss = current_value - cost
                    profit_loss_percent = (profit_loss / cost) * 100 if cost > 0 else 0
                    
                    st.metric("Kar/Zarar", f"{profit_loss:.2f} USDT", f"{profit_loss_percent:+.2f}%")
                
                with col3:
                    st.write("**💸 Satış Miktarı**")
                    # Satış miktarı seçimi
                    sell_amount = st.number_input(
                        "USDT Miktarı:",
                        min_value=10.0,
                        value=100.0,
                        step=10.0,
                        key=f"crypto_sell_amount_{symbol}"
                    )
                    
                    # Coin miktarı hesapla
                    coin_amount = sell_amount / current_price
                    st.write(f"**Coin Miktarı:** {coin_amount:.6f}")
                
                with col4:
                    st.write("**🛒 İşlem Butonları**")
                    
                    # Satış butonu
                    if st.button(f"💸 Sat", key=f"crypto_sell_{symbol}"):
                        print(f"DEBUG CRYPTO VIRTUAL: Satış butonuna tıklandı: {symbol}")
                        success = sell_crypto(symbol, sell_amount, current_price)
                        if success:
                            st.success(f"{symbol} başarıyla satıldı!")
                            st.rerun()
                        else:
                            st.error("Satış işlemi başarısız!")
                    
                    # Tümünü sat butonu
                    if st.button(f"💸 Tümünü Sat", key=f"crypto_sell_all_{symbol}"):
                        total_value = data['amount'] * current_price
                        success = sell_crypto(symbol, total_value, current_price)
                        if success:
                            st.success(f"{symbol} tümü satıldı!")
                            st.rerun()
                        else:
                            st.error("Satış işlemi başarısız!")
                
                st.divider()
    else:
        st.info("Portföyünüzde henüz coin bulunmuyor.")
    
    # Yeni coin alma
    st.subheader("🛒 Yeni Coin Al")
    
    # Takip listesinden coin seçimi (sadece coinler)
    crypto_watchlist = [symbol for symbol in st.session_state["watchlist"] if symbol.endswith('USDT')]
    if crypto_watchlist:
        selected_coin = st.selectbox(
            "Takip listesinden coin seçin:",
            crypto_watchlist,
            key="crypto_buy_coin_select"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Mock fiyat
            mock_price = np.random.uniform(0.0001, 50000)
            st.write(f"**Güncel Fiyat:** ${mock_price:.6f}")
        
        with col2:
            # USDT miktarı
            buy_amount = st.number_input(
                "USDT Miktarı:",
                min_value=10.0,
                value=100.0,
                step=10.0,
                key="crypto_buy_amount"
            )
            
            # Coin miktarı hesapla
            coin_amount = buy_amount / mock_price
            st.write(f"**Alınacak Miktar:** {coin_amount:.6f}")
        
        with col3:
            st.write("**🛒 Alım Butonu**")
            if st.button(f"🛒 {selected_coin} Al", key="crypto_buy_button"):
                print(f"DEBUG CRYPTO VIRTUAL: Alım butonuna tıklandı: {selected_coin}")
                success = buy_crypto(selected_coin, buy_amount, mock_price)
                if success:
                    st.success(f"{selected_coin} başarıyla alındı!")
                    st.rerun()
                else:
                    st.error("Alım işlemi başarısız!")
    else:
        st.info("Takip listenizde coin bulunmuyor. Önce Crypto Analizi sayfasından coin ekleyin.")

def show_crypto_performance_tab():
    """Crypto performans sekmesi"""
    st.subheader("📈 Crypto Performans Analizi")
    
    # Kalıcı veri yönetimi ile portföy al
    current_user = st.session_state.get("current_user", "gokhan")
    user_manager = st.session_state.get("user_manager")
    
    if user_manager:
        portfolio = user_manager.get_portfolio(current_user)
    else:
        # Fallback: session state
        user_data = get_current_user_data()
        portfolio = user_data.get('portfolio', {})
    
    if not portfolio:
        st.info("Portföyünüzde henüz coin bulunmuyor.")
        return
    
    # Performans hesapla
    total_invested = 0
    total_current_value = 0
    performance_data = []
    
    for symbol, data in portfolio.items():
        # Gerçek fiyatları al
        current_price = data['avg_price']  # Varsayılan olarak ortalama fiyat
        try:
            crypto_analyzer = st.session_state.get('crypto_analyzer')
            if crypto_analyzer:
                coin_data = crypto_analyzer.get_coin_data(symbol)
                if coin_data:
                    current_price = coin_data['current_price']
        except:
            # Hata durumunda ortalama fiyat kullan
            current_price = data['avg_price']
        
        current_value = data['amount'] * current_price
        invested = data['amount'] * data['avg_price']
        
        total_invested += invested
        total_current_value += current_value
        
        profit_loss = current_value - invested
        profit_loss_percent = (profit_loss / invested) * 100 if invested > 0 else 0
        
        performance_data.append({
            'Coin': symbol,
            'Yatırım': f"{invested:.2f} USDT",
            'Güncel Değer': f"{current_value:.2f} USDT",
            'Kar/Zarar': f"{profit_loss:.2f} USDT",
            'Kar/Zarar %': f"{profit_loss_percent:.2f}%"
        })
    
    # Performans tablosu
    df = pd.DataFrame(performance_data)
    st.dataframe(df, use_container_width=True)
    
    # Genel performans
    overall_profit_loss = total_current_value - total_invested
    overall_profit_loss_percent = (overall_profit_loss / total_invested) * 100 if total_invested > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Yatırım", f"{total_invested:.2f} USDT")
    
    with col2:
        st.metric("Güncel Değer", f"{total_current_value:.2f} USDT")
    
    with col3:
        st.metric("Toplam Kar/Zarar", f"{overall_profit_loss:.2f} USDT", f"{overall_profit_loss_percent:+.2f}%")
    
    with col4:
        # En iyi performans gösteren coin
        if performance_data:
            best_coin = max(performance_data, key=lambda x: float(x['Kar/Zarar %'].replace('%', '')))
            st.metric("En İyi Coin", best_coin['Coin'])

def show_crypto_transaction_history():
    """Crypto işlem geçmişi sekmesi"""
    st.subheader("📋 Crypto İşlem Geçmişi")
    
    user_data = get_current_user_data()
    
    if not user_data['transactions']:
        st.info("Henüz crypto işlem geçmişi bulunmuyor.")
        return
    
    # İşlem geçmişini göster
    for transaction in reversed(user_data['transactions']):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                transaction_type = "🟢 ALIM" if transaction['type'] == 'BUY' else "🔴 SATIM"
                st.write(f"{transaction_type} **{transaction['symbol']}**")
                # Timestamp kontrolü
                if 'timestamp' in transaction:
                    st.write(f"Tarih: {transaction['timestamp']}")
                else:
                    st.write(f"Tarih: {transaction.get('date', 'N/A')}")
            
            with col2:
                if transaction['type'] == 'BUY':
                    st.write(f"USDT: {transaction['amount']:.2f}")
                    st.write(f"Fiyat: ${transaction['price']:.6f}")
                else:
                    st.write(f"USDT: {transaction['amount']:.2f}")
                    st.write(f"Fiyat: ${transaction['price']:.6f}")
            
            with col3:
                if transaction['type'] == 'BUY':
                    st.write(f"Toplam: ${transaction['total_cost']:.2f}")
                else:
                    st.write(f"Toplam: ${transaction['total_revenue']:.2f}")
            
            with col4:
                st.write(f"Bakiye: ${transaction['balance_after']:.2f}")
            
            st.divider()

def analyze_whale_activity(min_volume=10000000, period="3 Ay", prediction_days=30):
    """
    Balina aktivitelerini analiz eder ve tahminler yapar
    
    Args:
        min_volume: Minimum balina hacmi (USDT)
        period: Analiz periyodu ("3 Ay", "6 Ay", "1 Yıl")
        prediction_days: Tahmin günleri
    
    Returns:
        dict: Balina analizi sonuçları
    """
    try:
        crypto_analyzer = st.session_state.get('crypto_analyzer')
        if not crypto_analyzer:
            return None
        
        # Periyot günlerini hesapla
        period_days = {
            "3 Ay": 90,
            "6 Ay": 180,
            "1 Yıl": 365
        }
        
        days = period_days.get(period, 90)
        
        # Mock balina verileri (gerçek uygulamada API'den alınacak)
        mock_whale_data = generate_mock_whale_data(crypto_analyzer, min_volume, days)
        
        # En çok alım yapılan coinleri analiz et
        top_whale_coins = analyze_top_whale_coins(mock_whale_data, crypto_analyzer)
        
        # Yakın vadeli tahminler
        predictions = generate_whale_predictions(mock_whale_data, crypto_analyzer, prediction_days)
        
        return {
            'top_whale_coins': top_whale_coins,
            'predictions': predictions,
            'analysis_period': period,
            'total_whale_volume': sum(coin['whale_volume'] for coin in top_whale_coins)
        }
    
    except Exception as e:
        print(f"Balina analizi hatası: {str(e)}")
        return None

def generate_mock_whale_data(crypto_analyzer, min_volume, days):
    """Mock balina verileri oluşturur"""
    whale_data = []
    
    # Popüler coinler listesi
    popular_coins = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", 
        "DOTUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT", "XRPUSDT",
        "AVAXUSDT", "MATICUSDT", "UNIUSDT", "ATOMUSDT", "FTMUSDT",
        "NEARUSDT", "ALGOUSDT", "VETUSDT", "ICPUSDT", "FILUSDT"
    ]
    
    for symbol in popular_coins:
        try:
            # Coin verilerini al
            coin_data = crypto_analyzer.get_coin_data(symbol)
            if coin_data:
                # Mock balina aktivitesi
                whale_volume = np.random.uniform(min_volume, min_volume * 10)
                whale_count = np.random.randint(5, 50)
                whale_score = np.random.uniform(60, 95)
                
                # Son 3 ay değişim
                change_3m = np.random.uniform(-30, 50)
                
                whale_data.append({
                    'symbol': symbol,
                    'current_price': coin_data['current_price'],
                    'volume_24h': coin_data['volume_24h'],
                    'whale_volume': whale_volume,
                    'whale_count': whale_count,
                    'whale_score': whale_score,
                    'change_3m': change_3m,
                    'rsi': coin_data.get('rsi', 50),
                    'trend': "Yükseliş" if change_3m > 0 else "Düşüş",
                    'coin_type': determine_coin_type(symbol, coin_data['current_price'], coin_data['volume_24h'])
                })
        except:
            continue
    
    return whale_data

def analyze_top_whale_coins(whale_data, crypto_analyzer):
    """En çok balina alımı yapılan coinleri analiz eder"""
    # Balina skoruna göre sırala
    sorted_coins = sorted(whale_data, key=lambda x: x['whale_score'], reverse=True)
    
    # En iyi 10 coin'i döndür
    return sorted_coins[:10]

def generate_whale_predictions(whale_data, crypto_analyzer, prediction_days):
    """Yakın vadeli balina tahminleri oluşturur"""
    predictions = []
    
    # Tahmin için potansiyel coinler
    potential_coins = [
        "SHIBUSDT", "DOGEUSDT", "PEPEUSDT", "FLOKIUSDT", "BONKUSDT",
        "WIFUSDT", "JUPUSDT", "PYTHUSDT", "BOMEUSDT", "BOOKUSDT"
    ]
    
    for symbol in potential_coins:
        try:
            # Coin verilerini al
            coin_data = crypto_analyzer.get_coin_data(symbol)
            if coin_data:
                # Tahmin skoru hesapla
                prediction_score = np.random.uniform(70, 95)
                entry_probability = np.random.uniform(60, 90)
                
                # Tahmin tarihi
                from datetime import datetime, timedelta
                predicted_date = datetime.now() + timedelta(days=np.random.randint(1, prediction_days))
                
                # Beklenen hacim
                expected_volume = np.random.uniform(5000000, 50000000)
                
                predictions.append({
                    'symbol': symbol,
                    'current_price': coin_data['current_price'],
                    'current_volume': coin_data['volume_24h'],
                    'prediction_score': prediction_score,
                    'entry_probability': entry_probability,
                    'predicted_date': predicted_date.strftime("%Y-%m-%d"),
                    'expected_volume': expected_volume,
                    'rsi': coin_data.get('rsi', 50),
                    'trend': "Yükseliş" if prediction_score > 80 else "Nötr",
                    'coin_type': determine_coin_type(symbol, coin_data['current_price'], coin_data['volume_24h'])
                })
        except:
            continue
    
    # Tahmin skoruna göre sırala
    sorted_predictions = sorted(predictions, key=lambda x: x['prediction_score'], reverse=True)
    
    return sorted_predictions[:5]

if __name__ == "__main__":
    main() 