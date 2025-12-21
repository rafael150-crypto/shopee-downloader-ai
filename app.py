import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="Estrategista de Achadinhos AI", page_icon="📈")

# Estilo focado em conversão
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { 
        width: 100%; border-radius: 25px; height: 3.5em; 
        background-color: #EE4D2D; color: white; 
        font-weight: bold; font-size: 1.1em; border: none;
    }
    .strategy-card { 
        background-color: #f9f9f9; padding: 20px; 
        border-radius: 15px; border: 1px solid #eeeeee;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Estrategista de Vendas AI")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0" # Certifique-se de usar sua chave real
genai.configure(api_key=API_KEY)

# O segredo está em usar apenas 'gemini-1.5-flash' sem o prefixo 'models/'
# A biblioteca cuida de colocar a versão v1 ou v1beta automaticamente
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. UPLOAD DO VÍDEO
st.markdown("### 📽️ Passo 1: Carregar Vídeo")
uploaded_file = st.file_uploader("Selecione o vídeo (sem marca d'água)", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ CRIAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 Analisando o produto..."):
                # Faz o upload do arquivo para o servidor do Gemini
                video_file = genai.upload_file(path=tfile.name)
                
                # Aguarda o processamento (obrigatório para vídeos)
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo de produto para YouTube Shorts/TikTok. Forneça:
                1. Três opções de títulos virais.
                2. Legenda persuasiva com emojis.
                3. 5 hashtags.
                4. Escreva apenas 'CAPA: X' (onde X é o segundo sugerido).
                """
                
                # Gera o conteúdo
                response = model.generate_content([video_file, prompt])
                res_text = response.text
                
                st.success("✅ Estratégia criada!")
                
                # Exibe o texto para copiar
                texto_limpo = "\n".join([l for l in res_text.split('\n') if "CAPA:" not in l])
                st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                st.code(texto_limpo, language="")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Processa a Capa
                match = re.search(r'CAPA:\s*(\d+)', res_text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap
