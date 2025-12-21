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
# Certifique-se de que esta é uma chave do Google AI Studio
API_KEY = "AIzaSyAR9yPU8zc-pOCWKWn5JCLy7ykvRXA2k8g"
genai.configure(api_key=API_KEY)

# --- SOLUÇÃO PARA O ERRO 404 ---
# Tentamos instanciar o modelo sem o prefixo 'models/' que causa o conflito
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo (sem marca d'água)", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Salvando temporariamente o vídeo
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 Analisando o produto..."):
                # Faz o upload para o Gemini
                video_file = genai.upload_file(path=tfile.name)
                
                # Aguarda o processamento pelo Google
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                if video_file.state.name == "FAILED":
                    st.error("O processamento do vídeo falhou no servidor do Google.")
                    st.stop()
                
                prompt = """
                Analise este vídeo de produto para redes sociais. Forneça:
                1. Três opções de títulos curtos e virais.
                2. Legenda persuasiva com foco em venda.
                3. 5 hashtags estratégicas.
                4. Escreva exatamente: 'CAPA: X' (onde X é o segundo sugerido).
                """
                
                # Gerando o conteúdo
                response = model.generate_content([video_file, prompt])
                
                st.success("✅ Estratégia criada!")
                
                # Exibindo o texto (removendo a parte da capa do texto principal)
                full_text = response.text
                clean_text = re.sub(r'CAPA:.*', '', full_text).strip()
                st.code(clean_text, language="")
                
                # Extraindo e exibindo a Capa
                match = re.search(r'CAPA:\s*(\d+)', full_text)
                segundo = int(match.group(1)) if match else 1
                
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                cap.release()
                
                # Limpando arquivo do Google
                genai.delete_file(video_file.name)
                
        except Exception as e:
            # Caso o erro 404 persista, damos uma instrução clara
            if "404" in str(e):
                st.error("Erro de Modelo (404): O Google não encontrou o modelo gemini-1.5-flash.")
                st.info("Tente substituir no código 'gemini-1.5-flash' por 'gemini-pro-vision' ou verifique sua chave API.")
            else:
                st.error(f"Erro na análise: {e}")
