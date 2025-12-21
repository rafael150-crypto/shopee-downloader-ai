import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="Estrategista AI", page_icon="📈")
st.title("📈 Estrategista de Vendas AI")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyAR9yPU8zc-pOCWKWn5JCLy7ykvRXA2k8g"
genai.configure(api_key=API_KEY)

# --- FUNÇÃO DE CONEXÃO SEGURA ---
def inicializar_modelo():
    # Tentamos os 3 nomes que o Google costuma aceitar sem erro 404
    for nome in ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-flash-latest"]:
        try:
            m = genai.GenerativeModel(nome)
            # Teste rápido de configuração
            return m
        except:
            continue
    return genai.GenerativeModel("gemini-1.5-flash")

model = inicializar_modelo()

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo do produto", type=["mp4", "mov"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 Analisando com conexão estável..."):
                # Upload para o servidor do Google
                video_file = genai.upload_file(path=tfile.name)
                
                # Aguarda processamento
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = "Analise este vídeo. Forneça 3 títulos virais, legenda persuasiva e 5 tags. Termine com 'CAPA: X'."
                
                # Chamada da IA
                response = model.generate_content([video_file, prompt])
                
                st.success("✅ Conteúdo gerado!")
                st.code(re.sub(r'CAPA:.*', '', response.text).strip())
                
                # Extração da Capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Sugestão de Capa")
                cap.release()
                
                # Limpa cota de armazenamento
                genai.delete_file(video_file.name)

        except Exception as e:
            if "404" in str(e):
                st.error("Erro 404: O modelo não foi encontrado. Tente criar uma NOVA chave de API no Google AI Studio.")
            elif "429" in str(e):
                st.warning("Limite atingido. Aguarde 60 segundos.")
            else:
                st.error(f"Erro: {e}")
