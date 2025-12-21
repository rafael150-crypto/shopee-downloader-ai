import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="Estrategista AI | Anti-Quota", page_icon="📈")
st.title("📈 Estrategista de Vendas AI")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyAR9yPU8zc-pOCWKWn5JCLy7ykvRXA2k8g"
genai.configure(api_key=API_KEY)

# --- SELEÇÃO DE MODELO ESTÁVEL ---
# O 1.5 Flash é muito mais tolerante a limites do que o 2.0 no plano grátis
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo do produto", type=["mp4", "mov"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 Analisando..."):
                # Upload para o servidor
                video_file = genai.upload_file(path=tfile.name)
                
                # Aguarda processamento
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = "Analise este vídeo de produto. Forneça 3 títulos virais, legenda persuasiva e 5 tags. Termine com 'CAPA: X'."
                
                # Tenta gerar o conteúdo
                response = model.generate_content([video_file, prompt])
                
                st.success("✅ Conteúdo gerado!")
                st.code(re.sub(r'CAPA:.*', '', response.text).strip())
                
                # Capa
                match = re.search(r'CAPA:\s*(\d+)', response.text)
                segundo = int(match.group(1)) if match else 1
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Sugestão de Capa")
                cap.release()
                
                # Limpa armazenamento no Google
                genai.delete_file(video_file.name)

        except Exception as e:
            if "429" in str(e):
                st.error("🚨 LIMITE DE COTA ATINGIDO!")
                st.warning("O Google exige uma pausa entre as análises. Por favor, aguarde 60 segundos antes de tentar novamente.")
                st.info("Dica: Se você usa muito, considere criar uma nova API Key em uma conta Google diferente.")
            else:
                st.error(f"Erro na análise: {e}")
