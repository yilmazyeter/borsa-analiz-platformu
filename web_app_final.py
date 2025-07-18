import streamlit as st
from datetime import datetime

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Borsa Analiz Platformu - Final",
    page_icon="📈",
    layout="wide"
)

# Session state başlatma
if 'button_clicks' not in st.session_state:
    st.session_state.button_clicks = 0
if 'opportunities_shown' not in st.session_state:
    st.session_state.opportunities_shown = False

st.title("📈 Borsa Analiz Platformu - Final Test")

# Debug paneli
with st.expander("🔍 Debug Bilgileri"):
    st.write(f"Button clicks: {st.session_state.button_clicks}")
    st.write(f"Opportunities shown: {st.session_state.opportunities_shown}")
    
    if st.button("Clear Debug"):
        st.session_state.button_clicks = 0
        st.session_state.opportunities_shown = False
        st.rerun()

# Analiz parametreleri
col1, col2, col3 = st.columns(3)

with col1:
    market = st.selectbox("Piyasa Seçin:", ["both", "bist", "us"], 
                         format_func=lambda x: {"both": "BIST + ABD", "bist": "BIST", "us": "ABD"}[x])

with col2:
    min_decline = st.slider("Minimum Düşüş (%)", 20, 80, 40)

with col3:
    max_results = st.slider("Maksimum Sonuç", 5, 20, 10)

# Analiz butonu
if st.button("🚀 Fırsatları Analiz Et", type="primary"):
    st.write("🔍 DEBUG: Fırsat analizi butonuna basıldı!")
    st.session_state.opportunities_shown = True
    st.success("✅ Fırsat analizi tamamlandı!")
    st.rerun()

# Fırsatları göster
if st.session_state.opportunities_shown:
    st.subheader("🔥 Bulunan Fırsatlar")
    
    # Mock fırsat verileri
    opportunities = [
        {'symbol': 'THYAO.IS', 'market': 'BIST', 'score': 85, 'price': 45.20, 'change': -15.5},
        {'symbol': 'GARAN.IS', 'market': 'BIST', 'score': 72, 'price': 28.50, 'change': -12.3},
        {'symbol': 'ASELS.IS', 'market': 'BIST', 'score': 68, 'price': 15.80, 'change': -18.7},
        {'symbol': 'AAPL', 'market': 'NASDAQ', 'score': 65, 'price': 175.30, 'change': -8.2}
    ]
    
    for i, opp in enumerate(opportunities):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{opp['symbol']}** - {opp['market']}")
            st.write(f"Skor: {opp['score']} | Fiyat: {opp['price']} | Değişim: {opp['change']}%")
        
        with col2:
            if st.button(f"📈 Takibe Al", key=f"btn_{opp['symbol']}_{i}"):
                st.session_state.button_clicks += 1
                st.write(f"🔍 DEBUG: BUTONA TIKLANDI! - {opp['symbol']}")
                st.write(f"🔍 DEBUG: Button clicks: {st.session_state.button_clicks}")
                st.success(f"✅ {opp['symbol']} takip listesine eklendi!")
                st.rerun()
        
        with col3:
            st.button(f"💰 Gökhan Al", key=f"gokhan_{opp['symbol']}")
        
        with col4:
            st.button(f"💰 Yılmaz Al", key=f"yilmaz_{opp['symbol']}")
        
        st.divider()

# Ana sayfa mesajı
if not st.session_state.opportunities_shown:
    st.info("👆 Yukarıdaki 'Fırsatları Analiz Et' butonuna basarak analiz başlatın.") 