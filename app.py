import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot AI", page_icon="🎬", layout="centered")

st.title("🚀 Gerador Viral: Shopee & Shorts")
st.write("Suba o vídeo da Shopee para remover marca d'água (IA) e gerar estratégia.")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0" # Coloque sua chave aqui
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo baixado da Shopee", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    # Exibir o vídeo original
    st.video(tfile.name)

    # Botão de Download (Para garantir que você tem o arquivo salvo)
    with open(tfile.name, "rb") as f:
        st.download_button(
            label="💾 SALVAR VÍDEO NA GALERIA",
            data=f,
            file_name="video_viral.mp4",
            mime="video/mp4"
        )

    # 3. ANÁLISE DA IA
    if st.button("✨ GERAR TÍTULO, HASHTAGS E CAPA"):
        try:
            with st.spinner("🤖 IA analisando o vídeo..."):
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo. Retorne APENAS:
                1. Título viral com emojis (estilo YouTube Shorts).
                2. Uma linha com 5 hashtags.
                3. Uma frase de descrição.
                4. 'CAPA: X' (segundo sugerido para o print).
                NÃO use rótulos.
                """
                
                response = model.generate_content([video_file, prompt])
                res_text = response.text
                
                # Exibir Texto Limpo
                texto_limpo = "\n".join([l for l in res_text.split('\n') if "CAPA:" not in l])
                st.subheader("📝 Conteúdo para Copiar")
                st.code(texto_limpo, language="") # st.code facilita copiar no celular

                # Extrair e Mostrar Capa
                match = re.search(r'CAPA:\s*(\d+)', res_text)
                segundo = int(match.group(1)) if match else 1
                
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                cap.release()

        except Exception as e:
            st.error(f"Erro na IA: {e}")
