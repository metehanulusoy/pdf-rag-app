import streamlit as st
from dotenv import load_dotenv
from rag import pdf_isle, soru_sor, ozet_cikar

load_dotenv()

st.set_page_config(
    page_title="PDF Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 PDF Assistant")
st.markdown("Upload your documents and let AI answer your questions.")
st.divider()

with st.sidebar:
    st.header("⚙️ Settings")
    
    dil = st.selectbox("🌍 Response language", ["Turkish", "English", "German", "French"])
    
    st.divider()
    
    st.header("📂 Upload Document")
    uploaded_files = st.file_uploader(
        "Select PDF (multiple allowed)",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        dosya_isimleri = [f.name for f in uploaded_files]
        
        if "vectordb" not in st.session_state or st.session_state.get("dosya_listesi") != dosya_isimleri:
            with st.spinner("Processing PDF..."):
                st.session_state.vectordb = pdf_isle(uploaded_files)
                st.session_state.dosya_listesi = dosya_isimleri
                st.session_state.mesajlar = []
                st.session_state.ozet = None
            st.success(f"✅ {len(uploaded_files)} document(s) ready!")
        
        for f in uploaded_files:
            st.caption(f"📄 {f.name}")
        
        st.divider()
        
        if st.button("📊 Generate Summary", use_container_width=True):
            with st.spinner("Summarizing..."):
                uploaded_files[0].seek(0)
                st.session_state.ozet = ozet_cikar(uploaded_files[0], dil)
        
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if "vectordb" not in st.session_state:
    st.info("👈 Upload a PDF from the left panel to get started.")
    
else:
    if st.session_state.get("ozet"):
        with st.expander("📊 Document Summary", expanded=True):
            st.write(st.session_state.ozet)
        st.divider()
    
    st.markdown("#### ⚡ Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📌 Summarize document", use_container_width=True):
            st.session_state.hizli_soru = "Summarize this document briefly."
    with col2:
        if st.button("🔑 What are the main topics?", use_container_width=True):
            st.session_state.hizli_soru = "What are the main topics in this document?"
    with col3:
        if st.button("📋 Key points", use_container_width=True):
            st.session_state.hizli_soru = "What are the most important points in this document?"

    st.divider()

    if "mesajlar" not in st.session_state:
        st.session_state.mesajlar = []

    for mesaj in st.session_state.mesajlar:
        with st.chat_message(mesaj["rol"]):
            st.write(mesaj["icerik"])

    soru = st.chat_input("Type your question...")
    
    if "hizli_soru" in st.session_state:
        soru = st.session_state.hizli_soru
        del st.session_state.hizli_soru

    if soru:
        st.session_state.mesajlar.append({"rol": "user", "icerik": soru})
        with st.chat_message("user"):
            st.write(soru)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                yanit = soru_sor(st.session_state.vectordb, soru, dil)
            st.write(yanit)
            
        st.session_state.mesajlar.append({"rol": "assistant", "icerik": yanit})
        st.rerun()