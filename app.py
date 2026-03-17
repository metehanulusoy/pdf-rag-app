import streamlit as st
from dotenv import load_dotenv
from rag import pdf_isle, soru_sor, ozet_cikar

load_dotenv()

st.set_page_config(
    page_title="PDF Asistan",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 PDF Asistan")
st.markdown("Belgelerinizi yükleyin, yapay zeka sizin için yanıtlasın.")
st.divider()

with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    dil = st.selectbox("🌍 Yanıt dili", ["Türkçe", "English", "Deutsch", "Français"])
    
    st.divider()
    
    st.header("📂 Belge Yükle")
    uploaded_files = st.file_uploader(
        "PDF seç (birden fazla olabilir)",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        dosya_isimleri = [f.name for f in uploaded_files]
        
        if "vectordb" not in st.session_state or st.session_state.get("dosya_listesi") != dosya_isimleri:
            with st.spinner("PDF işleniyor..."):
                st.session_state.vectordb = pdf_isle(uploaded_files)
                st.session_state.dosya_listesi = dosya_isimleri
                st.session_state.mesajlar = []
                st.session_state.ozet = None
            st.success(f"✅ {len(uploaded_files)} belge hazır!")
        
        for f in uploaded_files:
                st.caption(f"📄 {f.name}")
        
        st.divider()
        
        if st.button("📊 Özet Çıkar", use_container_width=True):
            with st.spinner("Özetleniyor..."):
                uploaded_files[0].seek(0)
                st.session_state.ozet = ozet_cikar(uploaded_files[0], dil)
        
        if st.button("🗑️ Sıfırla", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# Ana alan
if "vectordb" not in st.session_state:
    st.info("👈 Sol taraftan PDF yükleyerek başlayın.")
    
else:
    # Özet göster
    if st.session_state.get("ozet"):
        with st.expander("📊 Belge Özeti", expanded=True):
            st.write(st.session_state.ozet)
        st.divider()
    
    # Sık sorulan sorular
    st.markdown("#### ⚡ Hızlı Sorular")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📌 Belgeyi özetle", use_container_width=True):
            st.session_state.hizli_soru = "Bu belgeyi kısaca özetle."
    with col2:
        if st.button("🔑 Ana konular neler?", use_container_width=True):
            st.session_state.hizli_soru = "Bu belgedeki ana konular nelerdir?"
    with col3:
        if st.button("📋 Önemli noktalar", use_container_width=True):
            st.session_state.hizli_soru = "Bu belgedeki en önemli noktalar nelerdir?"

    st.divider()

    # Sohbet geçmişi
    if "mesajlar" not in st.session_state:
        st.session_state.mesajlar = []

    for mesaj in st.session_state.mesajlar:
        with st.chat_message(mesaj["rol"]):
            st.write(mesaj["icerik"])

    # Hızlı soru veya normal soru
    soru = st.chat_input("Sorunuzu yazın...")
    
    if "hizli_soru" in st.session_state:
        soru = st.session_state.hizli_soru
        del st.session_state.hizli_soru

    if soru:
        st.session_state.mesajlar.append({"rol": "user", "icerik": soru})
        with st.chat_message("user"):
            st.write(soru)

        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                yanit = soru_sor(st.session_state.vectordb, soru, dil)
            st.write(yanit)
            
        st.session_state.mesajlar.append({"rol": "assistant", "icerik": yanit})
        st.rerun()