import streamlit as st
from datetime import datetime

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Borsa Analiz Platformu - Basit",
    page_icon="📈",
    layout="wide"
)

# Session state başlatma
if 'button_clicks' not in st.session_state:
    st.session_state.button_clicks = 0
if 'opportunities' not in st.session_state:
    st.session_state.opportunities = []

st.title("📈 Borsa Analiz Platformu - Basit Test")

# Debug paneli
with st.expander("🔍 Debug Bilgileri"):
    st.write(f"Button clicks: {st.session_state.button_clicks}")
    st.write(f"Opportunities count: {len(st.session_state.opportunities)}")
    
    if st.button("Clear Debug"):
        st.session_state.button_clicks = 0
        st.session_state.opportunities = []
        st.rerun()

# Fırsat analizi butonu
if st.button("🚀 Fırsatları Analiz Et", type="primary"):
    st.write("🔍 DEBUG: Fırsat analizi butonuna basıldı!")
    
    # Mock fırsat verileri
    mock_opportunities = [
        {'symbol': 'THYAO.IS', 'market': 'BIST', 'score': 85},
        {'symbol': 'GARAN.IS', 'market': 'BIST', 'score': 72},
        {'symbol': 'ASELS.IS', 'market': 'BIST', 'score': 68},
        {'symbol': 'AAPL', 'market': 'NASDAQ', 'score': 65}
    ]
    
    st.session_state.opportunities = mock_opportunities
    st.success(f"✅ {len(mock_opportunities)} fırsat bulundu!")
    st.rerun()

# Fırsatları göster
if st.session_state.opportunities:
    st.subheader("🔥 Bulunan Fırsatlar")
    
    for i, opp in enumerate(st.session_state.opportunities):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{opp['symbol']}** - {opp['market']} - Skor: {opp['score']}")
        
        with col2:
            if st.button(f"📈 Takibe Al", key=f"btn_{opp['symbol']}_{i}"):
                st.session_state.button_clicks += 1
                st.write(f"🔍 DEBUG: BUTONA TIKLANDI! - {opp['symbol']}")
                st.write(f"🔍 DEBUG: Button clicks: {st.session_state.button_clicks}")
                st.success(f"✅ {opp['symbol']} takip listesine eklendi!")
                st.rerun()
        
        with col3:
            st.write(f"💰 Al")
        
        st.divider()

# Ana sayfa mesajı
if not st.session_state.opportunities:
    st.info("👆 Yukarıdaki 'Fırsatları Analiz Et' butonuna basarak analiz başlatın.") 