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
        # --- PASSO 1: SEGUIR LINK CURTO ---
        if "shp.ee" in url_input or "shopee.com.br" in url_input:
            with st.spinner("🔍 Decodificando link da Shopee..."):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                # Segue o redirecionamento até o final para pegar a URL gigante
                response = requests.get(url_input, headers=headers, allow_redirects=True, timeout=10)
                url_final = response.url
                
                # --- PASSO 2: EXTRAIR LINK DO VÍDEO DENTRO DA URL GIGANTE ---
                if "redir=" in url_final:
                    match = re.search(r'redir=([^&]+)', url_final)
                    if match:
                        video_url = urllib.parse.unquote(match.group(1))
                else:
                    video_url = url_final
                
                st.info(f"Link Real Localizado!")

        # --- PASSO 3: DOWNLOAD DO VÍDEO ---
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        ydl_opts = {
            'format': 'best',
            'outtmpl': tfile.name,
            'quiet': True,
            'nocheckcertificate': True,
        }

        with st.spinner("⏳ Baixando vídeo..."):
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
            st.error("Não foi possível baixar. Tente baixar o vídeo no app e subir manualmente abaixo.")

    except Exception as e:
        st.error(f"Erro ao processar link: {e}")

st.divider()
uploaded_file = st.file_uploader("Ou suba o vídeo manualmente:", type=["mp4"])
