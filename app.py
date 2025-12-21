import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="BrendaBot | Automação Achadinhos", page_icon="🚀")

# Estilo para os botões e interface
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .step-card { 
        background-color: white; padding: 20px; border-radius: 15px; 
        border-left: 5px solid #EE4D2D; margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .magic-link {
        display: block; width: 100%; text-align: center; background-color: #EE4D2D; 
        color: white !important; padding: 12px; border-radius: 10px; 
        text-decoration: none; font-weight: bold; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Robô Viral: Meio-Termo")

# --- PASSO 1: O ATALHO ---
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("1️⃣ Link da Shopee")
url_shopee = st.text_input("Cole o link aqui para gerar o atalho:")

if url_shopee:
    # Prepara o link para o SnapShopee (que é um dos mais rápidos hoje)
    # Alguns sites aceitam o link via parâmetro na URL
    link_atalho = f"https://snapshopee.app/pt?url={urllib.parse.quote(url_shopee)}"
    
    st.write("Clique no botão abaixo para baixar sem marca d'água:")
    st.markdown(f'<a href="{link_atalho}" target="_blank" class="magic-link">📥 BAIXAR VÍDEO AGORA</a>', unsafe_allow_html=True)
    st.caption("O site de download abrirá em outra aba com seu link já enviado.")
st.markdown('</div>', unsafe_allow_html=True)

# --- PASSO 2: A INTELIGÊNCIA ---
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("2️⃣ Análise Viral")
uploaded_file = st.file_uploader("Suba o vídeo baixado aqui:", type=["mp4", "mov"])

# Configuração da API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    if st.button("✨ GERAR TÍTULO, CAPA E LEGENDA"):
        try:
            with st.spinner("🤖 Analisando vídeo..."):
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo de produto e crie uma estratégia de vendas:
                1. Título 'Clickbait' ético com emojis.
                2. Legenda curta focada em dor/desejo.
                3. 5 Hashtags virais.
                4. Escreva 'CAPA: X' (segundo sugerido).
                """
                response = model.generate_content([video_file, prompt])
                
                st.success("✅ Estratégia Pronta!")
                st.code(response.text.split('CAPA:')[0], language="")
                
                # Capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Sugestão de Capa")
                cap.release()
        except Exception as e:
            st.error(f"Erro: {e}")
st.markdown('</div>', unsafe_allow_html=True)
