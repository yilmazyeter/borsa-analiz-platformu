import streamlit as st
import pandas as pd
import json
import os
import numpy as np
from datetime import datetime, timedelta
import logging
import yfinance as yf
from analysis.opportunity_analyzer import OpportunityAnalyzer
from bist_yfinance_integration import BISTYFinanceIntegration

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Session state başlatma
if 'button_clicks' not in st.session_state:
    st.session_state.button_clicks = 0
if 'opportunities_shown' not in st.session_state:
    st.session_state.opportunities_shown = False
if 'user_balance' not in st.session_state:
    st.session_state.user_balance = 10000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []

# Sanal Trading için gerekli session state'ler
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = "Gökhan"
if 'refresh_watchlist' not in st.session_state:
    st.session_state.refresh_watchlist = False
if 'users' not in st.session_state:
    st.session_state.users = {
        "Gökhan": {
            "balance": 100000.0,
            "portfolio": {},
            "transactions": [],
            "watchlist": []
        },
        "Yılmaz": {
            "balance": 100000.0,
            "portfolio": {},
            "transactions": [],
            "watchlist": []
        }
    }

# Mock hisse listeleri
bist_stocks = ["THYAO.IS", "GARAN.IS", "ASELS.IS", "AKBNK.IS", "EREGL.IS", "KCHOL.IS", "SAHOL.IS", "TUPRS.IS"]
us_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]

def get_current_user_data():
    """Seçili kullanıcının verilerini döndürür"""
    user = st.session_state.selected_user
    return st.session_state.users[user]

def update_user_data(user_data):
    """Kullanıcı verilerini günceller"""
    user = st.session_state.selected_user
    st.session_state.users[user] = user_data

def buy_stock_virtual(symbol, price, quantity=1):
    """Hisse satın alır (Sanal Trading için)"""
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

def sell_stock_virtual(symbol, price, quantity=None):
    """Hisse satar (Sanal Trading için)"""
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

def remove_from_watchlist(symbol):
    """Takip listesinden hisse çıkarır"""
    if symbol in st.session_state.watchlist:
        st.session_state.watchlist.remove(symbol)
        st.session_state.refresh_watchlist = True
        return True
    return False

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
                    success, message = buy_stock_virtual(symbol, mock_price, quantity)
                    if success:
                        st.success(f"{symbol} başarıyla alındı!")
                        st.rerun()
                    else:
                        st.error(message)
                
                # Satış butonu (portföyde varsa)
                user_data = get_current_user_data()
                if symbol in user_data['portfolio']:
                    if st.button(f"💸 Sat", key=f"watchlist_sell_{symbol}"):
                        success, message = sell_stock_virtual(symbol, mock_price, quantity)
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
                        success, message = sell_stock_virtual(symbol, mock_price, sell_quantity)
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
            success, message = buy_stock_virtual(selected_stock, new_stock_price, new_stock_quantity)
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

def get_real_opportunities(market='both', min_decline=20):
    """Gerçek veri ile fırsat analizi"""
    try:
        analyzer = OpportunityAnalyzer()
        opportunities = analyzer.get_real_time_opportunities(market, min_decline)
        
        if not opportunities:
            # Eğer gerçek veri çekilemezse mock data kullan
            return load_mock_data()
        
        # DataFrame'e çevir
        data = []
        for opp in opportunities:
            data.append({
                'symbol': opp['symbol'],
                'name': opp.get('name', opp['symbol']),
                'market': opp['market'],
                'current_price': opp['current_price'],
                'change_percent': opp['total_change'],
                'volume': opp['avg_volume'],
                'score': opp['opportunity_score'],
                'opportunity_type': ', '.join(opp.get('opportunity_factors', ['Fırsat']))
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        logging.error(f"Gerçek veri çekme hatası: {str(e)}")
        return load_mock_data()

def load_mock_data():
    """Mock veri yükleme (yedek)"""
    mock_data = [
        {
            'symbol': 'THYAO.IS',
            'name': 'Türk Hava Yolları',
            'market': 'BIST',
            'current_price': 45.2,
            'change_percent': -15.5,
            'volume': 1500000,
            'score': 85,
            'opportunity_type': 'Düşüş Sonrası Toparlanma'
        },
        {
            'symbol': 'GARAN.IS',
            'name': 'Garanti Bankası',
            'market': 'BIST',
            'current_price': 28.5,
            'change_percent': -12.3,
            'volume': 2000000,
            'score': 72,
            'opportunity_type': 'Teknik Destek'
        },
        {
            'symbol': 'ASELS.IS',
            'name': 'Aselsan',
            'market': 'BIST',
            'current_price': 35.8,
            'change_percent': -18.7,
            'volume': 800000,
            'score': 91,
            'opportunity_type': 'Yüksek Potansiyel'
        },
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'market': 'ABD',
            'current_price': 175.5,
            'change_percent': -8.2,
            'volume': 50000000,
            'score': 78,
            'opportunity_type': 'Teknoloji Düşüşü'
        },
        {
            'symbol': 'TSLA',
            'name': 'Tesla Inc.',
            'market': 'ABD',
            'current_price': 245.3,
            'change_percent': -22.1,
            'volume': 30000000,
            'score': 88,
            'opportunity_type': 'Elektrikli Araç Trendi'
        }
    ]
    return pd.DataFrame(mock_data)

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

def buy_stock(symbol, price, user):
    """Hisse satın al"""
    if not symbol or symbol.strip() == "":
        st.error("❌ Hisse sembolü boş olamaz!")
        return
        
    if st.session_state.user_balance >= price:
        st.session_state.user_balance -= price
        
        if symbol not in st.session_state.portfolio:
            st.session_state.portfolio[symbol] = {'quantity': 1, 'avg_price': price}
        else:
            current_quantity = st.session_state.portfolio[symbol]['quantity']
            current_avg_price = st.session_state.portfolio[symbol]['avg_price']
            new_quantity = current_quantity + 1
            new_avg_price = ((current_quantity * current_avg_price) + price) / new_quantity
            st.session_state.portfolio[symbol] = {'quantity': new_quantity, 'avg_price': new_avg_price}
        
        # İşlem geçmişine ekle
        transaction = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'ALIM',
            'symbol': symbol,
            'price': price,
            'user': user
        }
        st.session_state.transaction_history.append(transaction)
        
        logging.info(f"{user} {symbol} hissesini {price} TL'ye satın aldı")
        st.success(f"✅ {user} {symbol} hissesini {price} TL'ye satın aldı!")
    else:
        st.error(f"❌ Yetersiz bakiye! Gerekli: {price} TL, Mevcut: {st.session_state.user_balance} TL")

def sell_stock(symbol, price, user):
    """Hisse sat"""
    if symbol in st.session_state.portfolio and st.session_state.portfolio[symbol]['quantity'] > 0:
        st.session_state.user_balance += price
        st.session_state.portfolio[symbol]['quantity'] -= 1
        
        if st.session_state.portfolio[symbol]['quantity'] == 0:
            del st.session_state.portfolio[symbol]
        
        # İşlem geçmişine ekle
        transaction = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'SATIM',
            'symbol': symbol,
            'price': price,
            'user': user
        }
        st.session_state.transaction_history.append(transaction)
        
        logging.info(f"{user} {symbol} hissesini {price} TL'ye sattı")
        st.success(f"✅ {user} {symbol} hissesini {price} TL'ye sattı!")
    else:
        st.error(f"❌ {symbol} hissesi portföyde bulunamadı!")

def main():
    st.set_page_config(
        page_title="Borsa Analiz Platformu",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Borsa Analiz Platformu")
    st.markdown("---")
    
    # Debug paneli
    with st.expander("🔍 Debug Bilgileri", expanded=True):
        st.write(f"Button clicks: {st.session_state.button_clicks}")
        st.write(f"Opportunities shown: {st.session_state.opportunities_shown}")
        
        # Opportunities data güvenli kontrol
        opportunities_data = st.session_state.get('opportunities_data')
        if opportunities_data is None:
            st.write("Opportunities data: None")
        else:
            st.write(f"Opportunities data: {len(opportunities_data)} fırsat")
        
        st.write(f"Watchlist: {st.session_state.watchlist}")
        st.write(f"Portfolio: {st.session_state.portfolio}")
        st.write(f"Transaction history: {len(st.session_state.transaction_history)} işlem")
        
        if st.button("Clear Debug"):
            st.session_state.button_clicks = 0
            st.session_state.opportunities_shown = False
            st.session_state.opportunities_data = None
            st.rerun()
    
    # Sidebar - Kullanıcı Bilgileri
    st.sidebar.header("👤 Kullanıcı Bilgileri")
    st.sidebar.metric("💰 Bakiye", f"{st.session_state.user_balance:.2f} TL")
    
    # Portföy özeti
    if st.session_state.portfolio:
        st.sidebar.subheader("📊 Portföy Özeti")
        total_value = 0
        for symbol, data in st.session_state.portfolio.items():
            quantity = data['quantity']
            avg_price = data['avg_price']
            current_price = 45.2  # Mock fiyat
            value = quantity * current_price
            total_value += value
            st.sidebar.write(f"{symbol}: {quantity} adet")
        
        st.sidebar.metric("📈 Toplam Değer", f"{total_value:.2f} TL")
    
    # Takip listesi
    if st.session_state.watchlist:
        st.sidebar.subheader("👀 Takip Listesi")
        for symbol in st.session_state.watchlist:
            st.sidebar.write(f"📈 {symbol}")
    
    # Ana içerik
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Fırsat Analizi", "💰 Hayali Alım-Satım", "📊 Portföy Yönetimi", "🎮 Sanal Trading"])
    
    with tab1:
        st.header("🚀 Fırsat Analizi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            market = st.selectbox(
                "Piyasa Seçin:",
                ["BIST + ABD", "BIST", "ABD"],
                index=0
            )
        
        with col2:
            min_drop = st.slider("Minimum Düşüş (%):", 5, 50, 20)
        
        with col3:
            max_results = st.slider("Maksimum Sonuç:", 3, 20, 5)
        
        # Fırsat analizi sonuçlarını session state'de sakla
        if 'opportunities_data' not in st.session_state:
            st.session_state.opportunities_data = None
        
        if st.button("🚀 Fırsatları Analiz Et", type="primary"):
            st.session_state.button_clicks += 1
            st.session_state.opportunities_shown = True
            logging.info("Fırsat analizi başlatıldı")
            
            # Market parametresini çevir
            market_param = 'both'
            if market == "BIST":
                market_param = 'bist'
            elif market == "ABD":
                market_param = 'us'
            
            # Gerçek veri çek
            with st.spinner("🔍 Fırsatlar analiz ediliyor..."):
                opportunities_df = get_real_opportunities(market_param, min_drop)
            
            # Filtreleme
            if market == "BIST":
                opportunities_df = opportunities_df[opportunities_df['market'] == 'BIST']
            elif market == "ABD":
                opportunities_df = opportunities_df[opportunities_df['market'] == 'ABD']
            
            opportunities_df = opportunities_df[opportunities_df['change_percent'] <= -min_drop]
            opportunities_df = opportunities_df.head(max_results)
            
            # Sonuçları session state'e kaydet
            st.session_state.opportunities_data = opportunities_df.to_dict('records')
            st.rerun()
        
        # Fırsatları göster
        if st.session_state.opportunities_data:
            st.subheader("🔥 Bulunan Fırsatlar")
            
            for row in st.session_state.opportunities_data:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
                    
                    with col1:
                        st.write(f"**{row['symbol']} - {row['market']}**")
                        st.write(f"*{row['name']}*")
                        st.write(f"Fırsat: {row['opportunity_type']}")
                    
                    with col2:
                        st.metric("Skor", f"{row['score']}")
                    
                    with col3:
                        st.metric("Fiyat", f"{row['current_price']}")
                        st.metric("Değişim", f"{row['change_percent']:.1f}%")
                    
                    with col4:
                        # Takibe Al butonu
                        if st.button(f"📈 Takibe Al", key=f"watch_{row['symbol']}"):
                            st.session_state.button_clicks += 1
                            logging.info(f"Takibe Al butonuna tıklandı: {row['symbol']}")
                            add_to_watchlist(row['symbol'])
                            st.rerun()
                        
                        # Gökhan Al butonu
                        if st.button(f"💰 Gökhan Al", key=f"buy_gokhan_{row['symbol']}"):
                            st.session_state.button_clicks += 1
                            logging.info(f"Gökhan Al butonuna tıklandı: {row['symbol']}")
                            buy_stock(row['symbol'], row['current_price'], "Gökhan")
                            st.rerun()
                        
                        # Yılmaz Al butonu
                        if st.button(f"💰 Yılmaz Al", key=f"buy_yilmaz_{row['symbol']}"):
                            st.session_state.button_clicks += 1
                            logging.info(f"Yılmaz Al butonuna tıklandı: {row['symbol']}")
                            buy_stock(row['symbol'], row['current_price'], "Yılmaz")
                            st.rerun()
                    
                    st.divider()
    
    with tab2:
        st.header("💰 Hayali Alım-Satım")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Hisse Satın Al")
            
            symbol = st.text_input("Hisse Sembolü:", placeholder="THYAO.IS")
            price = st.number_input("Fiyat (TL):", min_value=0.01, value=45.2, step=0.01)
            user = st.selectbox("Kullanıcı:", ["Gökhan", "Yılmaz"])
            
            if st.button("🛒 Satın Al", key="buy_stock_manual"):
                st.session_state.button_clicks += 1
                buy_stock(symbol, price, user)
                st.rerun()
        
        with col2:
            st.subheader("📉 Hisse Sat")
            
            if st.session_state.portfolio:
                sell_symbol = st.selectbox("Satılacak Hisse:", list(st.session_state.portfolio.keys()))
                sell_price = st.number_input("Satış Fiyatı (TL):", min_value=0.01, value=45.2, step=0.01, key="sell_price")
                sell_user = st.selectbox("Kullanıcı:", ["Gökhan", "Yılmaz"], key="sell_user")
                
                if st.button("💸 Sat", key="sell_stock_manual"):
                    st.session_state.button_clicks += 1
                    sell_stock(sell_symbol, sell_price, sell_user)
                    st.rerun()
            else:
                st.info("📊 Portföyde hisse bulunmuyor")
    
    with tab3:
        st.header("📊 Portföy Yönetimi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Mevcut Portföy")
            
            if st.session_state.portfolio:
                portfolio_data = []
                for symbol, data in st.session_state.portfolio.items():
                    current_price = 45.2  # Mock fiyat
                    quantity = data['quantity']
                    avg_price = data['avg_price']
                    total_cost = quantity * avg_price
                    current_value = quantity * current_price
                    profit_loss = current_value - total_cost
                    profit_loss_percent = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
                    
                    portfolio_data.append({
                        'Hisse': symbol,
                        'Adet': quantity,
                        'Ort. Maliyet': f"{avg_price:.2f}",
                        'Güncel Fiyat': f"{current_price:.2f}",
                        'Toplam Maliyet': f"{total_cost:.2f}",
                        'Güncel Değer': f"{current_value:.2f}",
                        'Kar/Zarar': f"{profit_loss:.2f}",
                        'Kar/Zarar %': f"{profit_loss_percent:.2f}%"
                    })
                
                portfolio_df = pd.DataFrame(portfolio_data)
                st.dataframe(portfolio_df, use_container_width=True)
            else:
                st.info("📊 Portföyde hisse bulunmuyor")
        
        with col2:
            st.subheader("📋 İşlem Geçmişi")
            
            if st.session_state.transaction_history:
                history_data = []
                for transaction in st.session_state.transaction_history[-10:]:  # Son 10 işlem
                    history_data.append({
                        'Tarih': transaction['date'],
                        'İşlem': transaction['type'],
                        'Hisse': transaction['symbol'],
                        'Fiyat': f"{transaction['price']:.2f}",
                        'Kullanıcı': transaction['user']
                    })
                
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True)
            else:
                st.info("📋 İşlem geçmişi bulunmuyor")
    
    with tab4:
        show_virtual_trading()

if __name__ == "__main__":
    main() 