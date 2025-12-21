import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
from yt_dlp import YoutubeDL

# Configuração da Página
st.set_page_config(page_title="Shopee Viral Downloader", page_icon="🛍️")
st.title("🛍️ Shopee Premium: Download & IA")

# Configurar API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0" # COLOQUE SUA CHAVE AQUI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Campo de Link
url = st.text_input("Cole o link do vídeo (Shopee, TikTok, Instagram...):")

if url:
    try:
        # 1. Configuração para Melhor Qualidade e Sem Marca D'água
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best', # Busca a melhor qualidade possível
            'outtmpl': tfile.name,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }

        with st.spinner("Extraindo vídeo em alta qualidade..."):
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Botão de Download do arquivo MP4 para o celular
            with open(tfile.name, "rb") as file:
                st.download_button(
                    label="📥 BAIXAR VÍDEO NO CELULAR (SEM MARCA D'ÁGUA)",
                    data=file,
                    file_name="video_shopee_limpo.mp4",
                    mime="video/mp4"
                )
            
            st.video(tfile.name) # Mostra o vídeo no site

        # 2. Análise da IA
        if st.button("✨ GERAR TÍTULO E CAPA VIRAL"):
            with st.spinner("IA Analisando conteúdo..."):
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise o vídeo para YouTube Shorts. Retorne:
                1. Título viral (com emojis).
                2. Linha com 5 hashtags.
                3. Descrição curta.
                4. Escreva apenas 'CAPA: X' (segundo sugerido).
                NÃO use rótulos como TITULO: ou HASHTAGS:.
                """
                response = model.generate_content([video_file, prompt])
                
                # Exibir Texto Limpo
                texto_ia = response.text
                texto_limpo = "\n".join([l for l in texto_ia.split('\n') if "CAPA:" not in l])
                st.subheader("📝 Conteúdo para Copiar")
                st.text_area("", texto_limpo, height=200)
                
                # Extrair Capa
                match = re.search(r'CAPA:\s*(\d+)', texto_ia)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader("🖼️ Sugestão de Capa")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cap.release()

    except Exception as e:
        st.error(f"Erro: Link inválido ou vídeo protegido. Detalhes: {e}")
