import streamlit as st
from datetime import datetime

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Test Uygulaması",
    page_icon="🧪",
    layout="wide"
)

# Session state başlatma
if 'test_clicks' not in st.session_state:
    st.session_state.test_clicks = 0
if 'test_messages' not in st.session_state:
    st.session_state.test_messages = []

st.title("🧪 Test Uygulaması")

# Test butonu
if st.button("Test Butonu", key="test_button"):
    st.session_state.test_clicks += 1
    msg = f"Test butonu tıklandı: {datetime.now()}"
    st.session_state.test_messages.append(msg)
    st.success("✅ Test butonu çalışıyor!")

# Debug bilgileri
st.subheader("Debug Bilgileri")
st.write(f"Toplam tıklama: {st.session_state.test_clicks}")
st.write(f"Mesaj sayısı: {len(st.session_state.test_messages)}")

if st.session_state.test_messages:
    st.write("Son mesajlar:")
    for msg in st.session_state.test_messages[-5:]:
        st.write(f"• {msg}")

# Temizle butonu
if st.button("Temizle", key="clear_test"):
    st.session_state.test_clicks = 0
    st.session_state.test_messages = []
    st.rerun()

# Takip listesi testi
st.subheader("Takip Listesi Testi")

test_symbols = ["THYAO.IS", "GARAN.IS", "ASELS.IS"]

for i, symbol in enumerate(test_symbols):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{symbol}** - Test hissesi")
    with col2:
        if st.button(f"Takibe Al", key=f"test_watch_{symbol}_{i}"):
            msg = f"Takibe al tıklandı: {symbol} at {datetime.now()}"
            st.session_state.test_messages.append(msg)
            st.success(f"✅ {symbol} test takip listesine eklendi!")
            st.rerun() 