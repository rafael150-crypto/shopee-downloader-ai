import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
import urllib.parse
from yt_dlp import YoutubeDL

# Configuração da Página
st.set_page_config(page_title="Shopee Viral Bot", page_icon="🛍️")
st.title("🛍️ Shopee Viral Bot")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

url_input = st.text_input("Cole o link do vídeo aqui:")

if url_input:
    # --- MOTOR DE DESCRIPTOGRAFIA DE LINK ---
    video_url = url_input
    if "redir=" in url_input:
        try:
            # Busca o link real dentro do código gigante
            match = re.search(r'redir=([^&]+)', url_input)
            if match:
                # Decodifica símbolos como %3A e %2F para : e /
                video_url = urllib.parse.unquote(match.group(1))
                st.info(f"Link Real Localizado: {video_url}")
        except Exception as e:
            st.warning("Falha ao limpar link automaticamente.")

    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Configuração para forçar o download ignorando restrições de link universal
        ydl_opts = {
            'format': 'best',
            'outtmpl': tfile.name,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
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
                    
                    st.subheader("📝 Copie para o YouTube:")
                    st.code("\n".join([l for l in response.text.split('\n') if "CAPA:" not in l]), language="")
                    
                    # Extração da Capa
                    match = re.search(r'CAPA:\s*(\d+)', response.text)
                    segundo = int(match.group(1)) if match else 1
                    cap = cv2.VideoCapture(tfile.name)
                    cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                    ret, frame = cap.read()
                    if ret:
                        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Sugestão de Capa")
                    cap.release()
        else:
            st.error("Erro: A Shopee bloqueou o download automático deste link.")

    except Exception as e:
        st.error(f"Erro técnico: {e}")

st.divider()
st.write("Dica: Se o link falhar, você pode baixar o vídeo pelo app da Shopee e subir aqui:")
uploaded_file = st.file_uploader("Upload Manual", type=["mp4"])
