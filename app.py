import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
import urllib.parse
import requests
from yt_dlp import YoutubeDL

# Configuração da Página
st.set_page_config(page_title="Shopee Viral Bot", page_icon="🛍️")
st.title("🛍️ Shopee Viral Bot")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

url_input = st.text_input("Cole o link (curto ou longo) aqui:")

if url_input:
    video_url = url_input
    
    try:
        # --- PASSO 1: DECODIFICAÇÃO ---
        if "shp.ee" in url_input or "shopee.com.br" in url_input:
            with st.spinner("🔍 Localizando vídeo..."):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                response = requests.get(url_input, headers=headers, allow_redirects=True, timeout=15)
                url_final = response.url
                
                if "redir=" in url_final:
                    match = re.search(r'redir=([^&]+)', url_final)
                    if match:
                        video_url = urllib.parse.unquote(match.group(1))
                else:
                    video_url = url_final

        # --- PASSO 2: DOWNLOAD COM DISFARCE (REFERER) ---
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # O segredo está nestas opções abaixo para enganar o bloqueio
        ydl_opts = {
            'format': 'best',
            'outtmpl': tfile.name,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'referer': 'https://shopee.com.br/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'add_header': ['Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8']
        }

        with st.spinner("⏳ Extraindo arquivo de vídeo..."):
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
        if os.path.exists(tfile.name) and os.path.getsize(tfile.name) > 0:
            st.success("✅ Vídeo capturado!")
            st.video(tfile.name)

            if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
                with st.spinner("🤖 IA Analisando..."):
                    video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                    while video_file.state.name == "PROCESSING":
                        time.sleep(2)
                        video_file = genai.get_file(video_file.name)
                    
                    prompt = "Analise este vídeo para YouTube Shorts. Forneça: Título viral com emojis, 5 hashtags e descrição curta. Termine com 'CAPA: X' (segundo sugerido)."
                    response = model.generate_content([video_file, prompt])
                    
                    st.subheader("📝 Conteúdo para o YouTube:")
                    st.code("\n".join([l for l in response.text.split('\n') if "CAPA:" not in l]), language="")
                    
                    match = re.search(r'CAPA:\s*(\d+)', response.text)
                    segundo = int(match.group(1)) if match else 1
                    cap = cv2.VideoCapture(tfile.name)
                    cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                    ret, frame = cap.read()
                    if ret:
                        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Sugestão de Capa")
                    cap.release()
        else:
            st.error("A Shopee bloqueou o download automático. Tente subir o arquivo manualmente abaixo.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

st.divider()
st.info("Plano B: Se o link falhar, baixe o vídeo no App da Shopee e suba aqui:")
uploaded_file = st.file_uploader("Upload do Vídeo", type=["mp4"])
