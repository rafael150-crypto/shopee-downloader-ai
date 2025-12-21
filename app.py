import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
import requests
import urllib.parse
from yt_dlp import YoutubeDL

# Configuração da Página
st.set_page_config(page_title="Shopee Viral Bot", page_icon="🛍️")
st.title("🛍️ Shopee Viral Bot")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 2. CAIXA DE LINK (DIÁLOGO)
st.subheader("🔗 Enviar por Link")
url_input = st.text_input("Cole o link da Shopee aqui:", placeholder="https://br.shp.ee/...")

# 3. UPLOAD MANUAL (CASO O LINK FALHE)
st.subheader("📁 Ou suba o arquivo")
uploaded_file = st.file_uploader("Se o link der erro, baixe no app e suba aqui:", type=["mp4", "mov"])

video_path = None

# Lógica para processar o Link
if url_input:
    try:
        tfile_link = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        # Tenta seguir o link curto
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url_input, headers=headers, allow_redirects=True, timeout=10)
        final_url = res.url
        
        # Se for link da Shopee com redirecionamento, tenta limpar
        if "redir=" in final_url:
            match = re.search(r'redir=([^&]+)', final_url)
            if match:
                final_url = urllib.parse.unquote(match.group(1))

        ydl_opts = {'format': 'best', 'outtmpl': tfile_link.name, 'quiet': True}
        
        with st.spinner("⏳ Tentando baixar pelo link..."):
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([final_url])
            video_path = tfile_link.name
            st.success("✅ Vídeo baixado pelo link!")
    except Exception:
        st.error("❌ Não foi possível baixar pelo link (Bloqueio da Shopee). Use a opção de Upload abaixo.")

# Lógica para processar o Upload (Se não houver link ou se o link falhar)
if uploaded_file and not video_path:
    tfile_upload = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile_upload.write(uploaded_file.read())
    video_path = tfile_upload.name
    st.success("✅ Vídeo carregado via Upload!")

# 4. ANÁLISE DA IA (COMUM PARA AMBOS)
if video_path:
    st.video(video_path)
    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 IA Analisando..."):
                video_file = genai.upload_file(path=video_path, mime_type="video/mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = "Analise para YouTube Shorts: Título viral com emojis, 5 hashtags e descrição. Termine com 'CAPA: X' (segundo sugerido)."
                response = model.generate_content([video_file, prompt])
                
                st.subheader("📝 Conteúdo Sugerido")
                st.code(response.text.split('CAPA:')[0], language="")
                
                # Mostrar Capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption=f"Sugestão de Capa (Seg {segundo})")
                cap.release()
        except Exception as e:
            st.error(f"Erro na IA: {e}")
