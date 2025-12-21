import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="Shopee Viral Bot", page_icon="🛍️")
st.title("🛍️ Shopee Viral Bot")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 2. INTERFACE DE ENTRADA
st.info("💡 Dica: Como a Shopee bloqueia links diretos, a forma mais rápida é baixar o vídeo no App da Shopee e subir o arquivo aqui.")

arquivo_video = st.file_uploader("Suba o vídeo da Shopee aqui", type=["mp4", "mov", "avi"])

# Se o usuário subir o arquivo
if arquivo_video:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(arquivo_video.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 IA Analisando o vídeo..."):
                # Enviar para o Gemini
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo da Shopee e crie:
                1. Um título impossível de não clicar (curiosidade).
                2. 5 hashtags de alto volume.
                3. Uma descrição curta que gere desejo de compra.
                4. Escreva 'CAPA: X' (onde X é o melhor segundo do vídeo).
                """
                
                response = model.generate_content([video_file, prompt])
                
                st.subheader("📝 Conteúdo para Copiar")
                st.code(response.text.split('CAPA:')[0], language="")
                
                # Gerar a imagem da capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader(f"🖼️ Sugestão de Capa (Seg {segundo})")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cap.release()
                
        except Exception as e:
            st.error(f"Erro na IA: {e}")
