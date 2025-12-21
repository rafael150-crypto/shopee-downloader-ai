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

# --- FUNÇÃO PARA PEGAR O MODELO DISPONÍVEL ---
def carregar_melhor_modelo():
    try:
        # Lista os modelos disponíveis para a sua chave
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioridade de escolha
        prioridade = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        
        for p in prioridade:
            if p in modelos_disponiveis:
                return genai.GenerativeModel(p)
        
        # Se não achar os nomes exatos, pega o primeiro que tiver 'gemini'
        for m in modelos_disponiveis:
            if 'gemini' in m:
                return genai.GenerativeModel(m)
    except Exception as e:
        st.error(f"Erro ao listar modelos: {e}")
    return genai.GenerativeModel('gemini-1.5-flash') # Fallback final

model = carregar_melhor_modelo()

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo do produto", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner(f"🤖 Analisando com o modelo: {model.model_name}"):
                # Upload para o servidor
                video_file = genai.upload_file(path=tfile.name)
                
                # Aguarda processamento
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                prompt = "Analise este vídeo de produto. Forneça 3 títulos virais, legenda persuasiva e 5 tags. Termine com 'CAPA: X' (segundo sugerido)."
                
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
                
                genai.delete_file(video_file.name)
        except Exception as e:
            st.error(f"Erro na análise: {e}")
