import streamlit as st

st.title("Basit Test Uygulaması")

# Session state başlat
if 'test_count' not in st.session_state:
    st.session_state.test_count = 0

# Basit buton testi
if st.button("Test Butonu"):
    st.session_state.test_count += 1
    st.write(f"Butona {st.session_state.test_count} kez basıldı!")

# Checkbox testi
if st.checkbox("Test Checkbox"):
    st.write("Checkbox işaretlendi!")

# Form testi
with st.form("test_form"):
    submitted = st.form_submit_button("Form Butonu")
    if submitted:
        st.write("Form gönderildi!")

# Session state göster
st.write(f"Session state test_count: {st.session_state.test_count}") 