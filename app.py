import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração
st.set_page_config(page_title="Estrategista AI", page_icon="🚀")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)

# Mudamos para o 1.5 Flash que tem mais cota disponível
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 Estrategista de Achadinhos")

uploaded_file = st.file_uploader("Selecione o vídeo", type=["mp4", "mov"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    if st.button("✨ GERAR ESTRATÉGIA"):
        try:
            with st.spinner("🤖 Analisando... (Se demorar, é por causa do limite do Google)"):
                video_file = genai.upload_file(path=tfile.name)
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = "Analise este vídeo de produto. Crie 3 títulos virais, legenda e 5 tags. Termine com CAPA: X."
                
                # TENTATIVA AUTOMÁTICA EM CASO DE ERRO 429
                try:
                    response = model.generate_content([video_file, prompt])
                except Exception as e:
                    if "429" in str(e):
                        st.warning("Limite atingido! Aguardando 30 segundos para tentar novamente...")
                        time.sleep(30)
                        response = model.generate_content([video_file, prompt])
                    else:
                        raise e

                st.success("Pronto!")
                st.code(response.text.split('CAPA:')[0])
                
                # Deleta para liberar cota de armazenamento
                genai.delete_file(video_file.name)
                
        except Exception as e:
            st.error(f"Erro: {e}")
            st.info("Dica: Se o erro de cota persistir, aguarde 1 minuto. O plano gratuito tem limites por minuto.")
