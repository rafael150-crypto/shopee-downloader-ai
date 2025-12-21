import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
import urllib.parse

# Configuração da Página
st.set_page_config(page_title="BrendaBot | SVDown AI", page_icon="🛍️")

# Estilo para os botões e interface profissional
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #EE4D2D; color: white; }
    .step-card { 
        background-color: white; padding: 25px; border-radius: 20px; 
        border: 1px solid #e1e4e8; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .svdown-btn {
        display: block; width: 100%; text-align: center; background-color: #000000; 
        color: #ffffff !important; padding: 15px; border-radius: 12px; 
        text-decoration: none; font-weight: bold; margin-top: 15px;
        font-size: 1.1em;
    }
    .svdown-btn:hover { background-color: #333333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Robô de Achadinhos Pro")
st.write("Siga os dois passos abaixo para criar seu vídeo viral.")

# --- PASSO 1: DOWNLOAD EXTERNO ---
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("1️⃣ Obter Vídeo sem Marca D'água")
url_shopee = st.text_input("Cole o link da Shopee aqui:", placeholder="https://br.shp.ee/...")

if url_shopee:
    # Gerando o Deep Link para o SVDown
    # O SVDown.tech aceita o parâmetro ?url= para facilitar o preenchimento
    link_svdown = f"https://svdown.tech/?url={urllib.parse.quote(url_shopee)}"
    
    st.info("Clique no botão abaixo. O link já será enviado para o SVDown!")
    st.markdown(f'<a href="{link_svdown}" target="_blank" class="svdown-btn">⚡ ABRIR SVDOWN AGORA</a>', unsafe_allow_html=True)
    st.caption("Após baixar o vídeo no SVDown, volte aqui para o Passo 2.")
st.markdown('</div>', unsafe_allow_html=True)

# --- PASSO 2: INTELIGÊNCIA ARTIFICIAL ---
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("2️⃣ Gerar Estratégia de Venda")
uploaded_file = st.file_uploader("Suba o vídeo limpo aqui:", type=["mp4", "mov"])

# Configuração da API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ CRIAR POST VIRAL"):
        try:
            with st.spinner("🤖 Analisando o produto..."):
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo de produto da Shopee. Forneça:
                1. Título 'Clickbait' impossível de ignorar (com emojis).
                2. Legenda curta com foco em benefício.
                3. 5 hashtags estratégicas.
                4. Escreva apenas 'CAPA: X' (X é o segundo ideal para a capa).
                """
                response = model.generate_content([video_file, prompt])
                
                st.success("✅ Estratégia Pronta!")
                # Exibindo o texto em uma caixa de código fácil de copiar no celular
                st.code(response.text.split('CAPA:')[0], language="")
                
                # Gerar imagem da capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader(f"🖼️ Sugestão de Capa (Seg {segundo})")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                cap.release()
                
        except Exception as e:
            st.error(f"Erro na IA: {e}")
st.markdown('</div>', unsafe_allow_html=True)
