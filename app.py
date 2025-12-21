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
st.set_page_config(page_title="Shopee Viral Downloader", page_icon="🛍️")
st.title("🛍️ Shopee Premium: Download & IA")

# 1. CONFIGURAÇÃO DA API
API_KEY = "SUA_NOVA_CHAVE_AQUI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

url_input = st.text_input("Cole o link do vídeo aqui:")

if url_input:
    # --- FUNÇÃO DE LIMPEZA DE LINK SHOPEE ---
    video_url = url_input
    if "redir=" in url_input:
        try:
            # Extrai o que está depois de 'redir='
            match = re.search(r'redir=([^&]+)', url_input)
            if match:
                video_url = urllib.parse.unquote(match.group(1))
                st.info(f"Link Real Extraído: {video_url}")
        except:
            pass
    # ---------------------------------------

    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Configuração para ignorar erros de SSL e redirecionamento
        ydl_opts = {
            'format': 'best',
            'outtmpl': tfile.name,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
        }

        with st.spinner("📥 Baixando vídeo limpo..."):
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if os.path.exists(tfile.name) and os.path.getsize(tfile.name) > 0:
                with open(tfile.name, "rb") as f:
                    st.download_button(
                        label="💾 SALVAR VÍDEO NA GALERIA (SEM LOGO)",
                        data=f,
                        file_name="shopee_video.mp4",
                        mime="video/mp4"
                    )
                st.video(tfile.name)

                # 2. BOTÃO DA IA
                if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
                    with st.spinner("🤖 IA analisando o vídeo..."):
                        video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                        while video_file.state.name == "PROCESSING":
                            time.sleep(2)
                            video_file = genai.get_file(video_file.name)
                        
                        prompt = "Analise para YouTube Shorts: Título viral com emojis, 5 hashtags e descrição curta. Termine com 'CAPA: X' (segundo sugerido)."
                        response = model.generate_content([video_file, prompt])
                        
                        texto_limpo = "\n".join([l for l in response.text.split('\n') if "CAPA:" not in l])
                        st.subheader("📝 Conteúdo para Copiar")
                        st.text_area("", texto_limpo, height=200)
                        
                        # Mostrar Capa
                        match = re.search(r'CAPA:\s*(\d+)', response.text)
                        segundo = int(match.group(1)) if match else 1
                        cap = cv2.VideoCapture(tfile.name)
                        cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                        ret, frame = cap.read()
                        if ret:
                            st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Sugestão de Capa")
                        cap.release()
            else:
                st.error("Não foi possível baixar o vídeo desse link. Tente outro formato de compartilhamento da Shopee.")

    except Exception as e:
        st.error(f"Erro no sistema: {e}")
