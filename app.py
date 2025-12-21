import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot | Achadinhos", page_icon="🛍️")

# Estilo Profissional
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .download-btn { 
        display: block; width: 100%; text-align: center; background-color: #00b894; 
        color: white; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Robô de Achadinhos Pro")

# --- PASSO 1: DOWNLOAD ---
st.subheader("1️⃣ Primeiro, baixe o vídeo sem marca d'água")
st.write("Copie o link da Shopee e use o site abaixo para baixar o vídeo limpo:")
st.markdown('<a href="https://svdown.com/" target="_blank" class="download-btn">🔗 ABRIR SVDOWN (BAIXAR VÍDEO)</a>', unsafe_allow_html=True)

st.divider()

# --- PASSO 2: IA ---
st.subheader("2️⃣ Agora, deixe a IA criar seu Post")
uploaded_file = st.file_uploader("Suba o vídeo que você baixou do SVDown", type=["mp4", "mov"])

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR TÍTULO, CAPA E TAGS"):
        try:
            with st.spinner("🤖 Analisando o produto..."):
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Atue como especialista em marketing de afiliados. Analise o vídeo e retorne:
                1. Título Viral com Emojis.
                2. 5 Hashtags de alto engajamento.
                3. Uma chamada para ação (CTA) para clicar no link da bio.
                4. 'CAPA: X' (X é o segundo exato para a melhor capa).
                NÃO use rótulos como TITULO:.
                """
                
                response = model.generate_content([video_file, prompt])
                
                st.success("📝 Conteúdo Pronto!")
                texto_limpo = "\n".join([l for l in response.text.split('\n') if "CAPA:" not in l])
                st.code(texto_limpo, language="")
                
                # Sugestão de Capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption=f"Sugestão de Capa no Segundo {segundo}")
                cap.release()
                
        except Exception as e:
            st.error(f"Erro na IA: {e}")
