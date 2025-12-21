import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="Estrategista de Achadinhos AI", page_icon="📈")

st.title("📈 Estrategista de Vendas AI")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyAR9yPU8zc-pOCWKWn5JCLy7ykvRXA2k8g"
genai.configure(api_key=API_KEY)

# --- FUNÇÃO PARA ENCONTRAR O MODELO DISPONÍVEL ---
def get_model():
    # Tentamos os nomes oficiais em ordem de prioridade
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro-vision']:
        try:
            m = genai.GenerativeModel(model_name)
            # Teste rápido de chamada
            return m
        except:
            continue
    return genai.GenerativeModel('gemini-1.5-flash') # Fallback padrão

model = get_model()

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo (sem marca d'água)", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ CRIAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 Analisando o produto..."):
                # Faz o upload para o Gemini
                video_file = genai.upload_file(path=tfile.name)
                
                # Aguarda o processamento
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = """
                Analise este vídeo de produto. Forneça:
                1. Três opções de títulos virais.
                2. Legenda persuasiva.
                3. 5 hashtags.
                4. Escreva apenas 'CAPA: X' (onde X é o segundo sugerido).
                """
                
                # Chamada da geração
                response = model.generate_content([video_file, prompt])
                
                st.success("✅ Estratégia criada!")
                st.code(response.text.split('CAPA:')[0])
                
                # Limpeza
                genai.delete_file(video_file.name)
                
        except Exception as e:
            st.error(f"Erro na análise: {e}")
            st.info("Dica: Se o erro persistir, verifique se sua chave API é do 'Google AI Studio'.")
