import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
from yt_dlp import YoutubeDL

# Configuração da Página
st.set_page_config(page_title="Shopee Viral Downloader", page_icon="🛍️", layout="centered")

# Estilização básica
st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛍️ Shopee Premium: Download & IA")
st.write("Baixe vídeos sem marca d'água e gere títulos virais para Shorts.")

# 1. CONFIGURAÇÃO DA API (COLOQUE SUA CHAVE ABAIXO)
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 2. OPÇÕES DE ENTRADA
opcao = st.radio("Como deseja enviar o vídeo?", ("Link da Shopee/Social", "Upload do Celular"))

video_path = None

if opcao == "Link da Shopee/Social":
    url_input = st.text_input("Cole o link do vídeo aqui:", placeholder="https://sv.shopee.com.br/share-video/...")
    if url_input:
        # Limpeza básica de links universais da Shopee
        if "redir=" in url_input:
            url_input = re.search(r'redir=(https%3A%2F%2F.+)', url_input).group(1)
            import urllib.parse
            url_input = urllib.parse.unquote(url_input)
            st.info(f"Link extraído: {url_input}")

        try:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            ydl_opts = {
                'format': 'best',
                'outtmpl': tfile.name,
                'quiet': True,
                'no_warnings': True,
            }
            with st.spinner("📥 Baixando vídeo em alta qualidade..."):
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url_input])
                video_path = tfile.name
                st.success("Vídeo baixado!")
        except Exception as e:
            st.error(f"Erro ao baixar: {e}")

else:
    uploaded_file = st.file_uploader("Selecione o vídeo da galeria", type=["mp4", "mov", "avi"])
    if uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        video_path = tfile.name

# 3. PROCESSAMENTO E IA
if video_path:
    # Botão de download do arquivo limpo para o celular
    with open(video_path, "rb") as f:
        st.download_button(
            label="💾 SALVAR VÍDEO NA GALERIA (SEM LOGO)",
            data=f,
            file_name="video_limpo.mp4",
            mime="video/mp4"
        )

    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 IA analisando o vídeo..."):
                # Upload para o Gemini
                video_file = genai.upload_file(path=video_path, mime_type="video/mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo para YouTube Shorts. Forneça:
                1. Um título viral (curiosidade + benefício) com emojis.
                2. Uma linha com 5 hashtags estratégicas.
                3. Uma descrição curta de uma linha.
                4. Escreva apenas 'CAPA: X' (onde X é o segundo de maior impacto).
                NÃO use rótulos como Título: ou Hashtags:.
                """
                
                response = model.generate_content([video_file, prompt])
                res_text = response.text
                
                # Exibir Texto para Copiar
                texto_limpo = "\n".join([l for l in res_text.split('\n') if "CAPA:" not in l])
                st.subheader("📝 Conteúdo para Copiar")
                st.text_area("", texto_limpo, height=200)
                
                # Exibir Sugestão de Capa
                match = re.search(r'CAPA:\s*(\d+)', res_text)
                segundo = int(match.group(1)) if match else 1
                
                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                cap.release()

        except Exception as e:
            st.error(f"Erro na análise da IA: {e}")

# Limpeza de arquivos temporários ao final (opcional)
if video_path and os.path.exists(video_path):
    pass # Mantemos o arquivo enquanto a sessão estiver ativa para o download_button funcionar
