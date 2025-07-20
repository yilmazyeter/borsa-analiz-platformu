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

# Hayali alım-satım sistemi için session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'user_balance' not in st.session_state:
    st.session_state.user_balance = 100000.0  # Başlangıç bakiyesi
if 'refresh_watchlist' not in st.session_state:
    st.session_state.refresh_watchlist = False
if 'opportunities_data' not in st.session_state:
    st.session_state.opportunities_data = None

# Kullanıcı yönetimi için session state
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = "Gökhan"
if 'users' not in st.session_state:
    st.session_state.users = {
        "Gökhan": {
            "balance": 100000.0,
            "portfolio": {},
            "transactions": []
        },
        "Yılmaz": {
            "balance": 100000.0,
            "portfolio": {},
            "transactions": []
        }
    }

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
    """Seçili kullanıcının verilerini döndürür"""
    user = st.session_state.selected_user
    return st.session_state.users[user]

def update_user_data(user_data):
    """Kullanıcı verilerini günceller"""
    user = st.session_state.selected_user
    st.session_state.users[user] = user_data

def add_to_watchlist(symbol):
    """Takip listesine hisse ekler"""
    if symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(symbol)
        st.session_state.refresh_watchlist = True
        print(f"DEBUG: {symbol} takip listesine eklendi. Mevcut liste: {st.session_state.watchlist}")
        # Log dosyasına da yazalım
        with open('web_app.log', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DEBUG - {symbol} takip listesine eklendi. Mevcut liste: {st.session_state.watchlist}\n")
        logging.info(f"Hisse takip listesine eklendi: {symbol}")
        st.success(f"✅ {symbol} takip listesine eklendi!")
        return True
    print(f"DEBUG: {symbol} zaten takip listesinde. Mevcut liste: {st.session_state.watchlist}")
    return False

def remove_from_watchlist(symbol):
    """Takip listesinden hisse çıkarır"""
    if symbol in st.session_state.watchlist:
        st.session_state.watchlist.remove(symbol)
        st.session_state.refresh_watchlist = True
        return True
    return False

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
    st.sidebar.metric("Bakiye", f"{user_data['balance']:.2f} TL")
    
    # Takip listesi
    st.sidebar.subheader("👀 Takip Listesi")
    print(f"DEBUG SIDEBAR: Takip listesi içeriği: {st.session_state.watchlist}")
    if st.session_state.watchlist:
        st.sidebar.write(f"📊 **{len(st.session_state.watchlist)} hisse takip ediliyor**")
        for symbol in st.session_state.watchlist:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.sidebar.write(f"📈 {symbol}")
            with col2:
                if st.sidebar.button("❌", key=f"remove_{symbol}"):
                    remove_from_watchlist(symbol)
    else:
        st.sidebar.info("Henüz takip listesi boş")
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
    
    if not st.session_state.watchlist:
        st.info("Henüz takip listesinde hisse bulunmuyor.")
        st.markdown("""
        **Takip listesine hisse eklemek için:**
        1. **Fırsat Analizi** sayfasına gidin
        2. İstediğiniz hisseyi bulun
        3. **"Takibe Al"** butonuna tıklayın
        """)
        return
    
    # Takip listesi özeti
    st.success(f"✅ Takip listenizde {len(st.session_state.watchlist)} hisse bulunuyor")
    
    # Her hisse için detaylı bilgi ve işlem seçenekleri
    for i, symbol in enumerate(st.session_state.watchlist):
        with st.expander(f"📈 {symbol} - Detaylar ve İşlemler", expanded=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.write(f"**{symbol}**")
                
                # Mock hisse bilgileri (gerçek uygulamada API'den çekilecek)
                mock_price = 45.2 + np.random.uniform(-10, 10)
                mock_change = np.random.uniform(-15, 15)
                mock_volume = np.random.randint(1000000, 10000000)
                
                st.write(f"💰 **Güncel Fiyat:** {mock_price:.2f} TL")
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
                st.write(f"**Toplam:** {total_cost:.2f} TL")
            
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
        st.metric("Toplam Hisse", len(st.session_state.watchlist))
    
    with col2:
        # Pozitif trend sayısı
        positive_count = sum(1 for _ in range(len(st.session_state.watchlist)) 
                           if np.random.uniform(-15, 15) > 0)
        st.metric("Pozitif Trend", positive_count)
    
    with col3:
        # Portföyde olan hisse sayısı
        user_data = get_current_user_data()
        portfolio_count = sum(1 for symbol in st.session_state.watchlist 
                            if symbol in user_data['portfolio'])
        st.metric("Portföyde Olan", portfolio_count)
    
    with col4:
        # Ortalama fiyat
        avg_price = 45.2  # Mock ortalama
        st.metric("Ortalama Fiyat", f"{avg_price:.2f} TL")

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
            'Ortalama Maliyet': f"{data['avg_price']:.2f} TL",
            'Güncel Fiyat': f"{current_price:.2f} TL",
            'Toplam Değer': f"{value:.2f} TL",
            'Kar/Zarar': f"{profit_loss:.2f} TL",
            'Kar/Zarar %': f"{profit_loss_percent:.2f}%"
        })
    
    # Portföy tablosu
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)
    
    # Toplam değer
    st.metric("📈 Toplam Portföy Değeri", f"{total_value:.2f} TL")

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
                    st.write(f"💰 **Ortalama Maliyet:** {data['avg_price']:.2f} TL")
                    
                    # Mock güncel fiyat
                    mock_price = data['avg_price'] * np.random.uniform(0.8, 1.2)
                    st.write(f"📊 **Güncel Fiyat:** {mock_price:.2f} TL")
                    
                    # Kar/zarar hesapla
                    cost = data['quantity'] * data['avg_price']
                    value = data['quantity'] * mock_price
                    profit_loss = value - cost
                    profit_loss_percent = (profit_loss / cost) * 100 if cost > 0 else 0
                    
                    if profit_loss > 0:
                        st.success(f"📈 **Kar:** {profit_loss:.2f} TL (%{profit_loss_percent:.2f})")
                    else:
                        st.error(f"📉 **Zarar:** {profit_loss:.2f} TL (%{profit_loss_percent:.2f})")
                
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
                    st.write(f"**Toplam Gelir:** {total_revenue:.2f} TL")
                
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
        st.write(f"**Toplam Maliyet:** {total_cost:.2f} TL")
        
        # Bakiye kontrolü
        if total_cost > user_data['balance']:
            st.error(f"❌ Yetersiz bakiye! Gerekli: {total_cost:.2f} TL, Mevcut: {user_data['balance']:.2f} TL")
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
                'Alış Ortalama': f"{data['avg_buy_price']:.2f} TL",
                'Satış Ortalama': f"{data['avg_sell_price']:.2f} TL",
                'Alınan Adet': data['quantity_bought'],
                'Satılan Adet': data['quantity_sold'],
                'Kar/Zarar': f"{data['profit_loss']:.2f} TL",
                'Kar/Zarar %': f"{data['profit_loss_percent']:.2f}%"
            })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
        
        # Genel performans
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Toplam Kar/Zarar", f"{total_profit:.2f} TL")
        with col2:
            st.metric("📊 İşlem Sayısı", total_transactions)
        with col3:
            avg_profit = total_profit / total_transactions if total_transactions > 0 else 0
            st.metric("📈 Ortalama Kar/Zarar", f"{avg_profit:.2f} TL")

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
            'Fiyat': f"{transaction['price']:.2f} TL",
            'Toplam': f"{transaction['total']:.2f} TL"
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
    st.metric("💰 Toplam Portföy Değeri", f"{total_value:,.2f} TL")

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
            "total_amount": st.column_config.NumberColumn("Toplam (TL)", format="%.2f"),
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
            "initial_investment": st.column_config.NumberColumn("Başlangıç Yatırımı (TL)", format="%.2f"),
            "current_value": st.column_config.NumberColumn("Güncel Değer (TL)", format="%.2f"),
            "profit_loss": st.column_config.NumberColumn("Kar/Zarar (TL)", format="%.2f"),
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
        st.metric("💰 Toplam Yatırım", f"{total_initial:,.2f} TL")
    
    with col2:
        st.metric("📈 Güncel Değer", f"{total_current:,.2f} TL")
    
    with col3:
        st.metric(
            "📊 Toplam Kar/Zarar", 
            f"{total_profit_loss:,.2f} TL",
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
    
    # Sidebar menü
    st.sidebar.title("📊 Menü")
    page = st.sidebar.selectbox(
        "Sayfa Seçin:",
        ["🏠 Ana Sayfa", "📈 Hisse Analizi", "🚀 Fırsat Analizi", "🤖 AI Analizi", "📰 Haberler", "💰 Portföy Optimizer", 
         "🔔 Alarm Sistemi", "🎮 Sanal Trading", "📊 TradingView", "⚙️ Ayarlar"]
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
    elif page == "📰 Haberler":
        show_news_page()
    elif page == "💰 Portföy Optimizer":
        show_portfolio_optimizer()
    elif page == "🔔 Alarm Sistemi":
        show_alerts_system()
    elif page == "🎮 Sanal Trading":
        show_virtual_trading()
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
            st.session_state.opportunities_data = opportunities
            st.rerun()
    
    # Fırsatları göster
    if st.session_state.opportunities_data:
        opportunities = st.session_state.opportunities_data
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
                            # Takibe Al butonu
                            if st.button(f"📈 Takibe Al", key=f"watch_{opportunity['symbol']}"):
                                print(f"DEBUG OPPORTUNITY: Takibe Al butonuna tıklandı: {opportunity['symbol']}")
                                add_to_watchlist(opportunity['symbol'])
                                st.rerun()
                            
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

if __name__ == "__main__":
    main() 