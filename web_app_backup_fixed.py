import streamlit as st
import pandas as pd
import json
import os
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
    """Hisseyi takip listesine ekle"""
    if symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(symbol)
        logging.info(f"Hisse takip listesine eklendi: {symbol}")
        st.success(f"✅ {symbol} takip listesine eklendi!")

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
    tab1, tab2, tab3 = st.tabs(["🚀 Fırsat Analizi", "💰 Hayali Alım-Satım", "📊 Portföy Yönetimi"])
    
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

if __name__ == "__main__":
    main() 