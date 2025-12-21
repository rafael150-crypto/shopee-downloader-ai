import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot AI | Estrategista Pro", page_icon="🚀")

# Estilo Premium
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.5em; 
        background-color: #EE4D2D; color: white; font-weight: bold;
    }
    .strategy-card { 
        background-color: #f8f9fa; padding: 20px; 
        border-radius: 15px; border: 1px solid #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Estrategista de Achadinhos AI")
st.write("Usando o poder do Gemini 2.0 para criar posts que vendem.")

# 1. CONFIGURAÇÃO DA API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)

# Escolha do Modelo: 'gemini-2.0-flash' ou 'gemini-1.5-pro'
# O 2.0 Flash é mais rápido e excelente para vídeos.
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    model = genai.GenerativeModel('gemini-1.5-flash')

# 2. UPLOAD DO VÍDEO
uploaded_file = st.file_uploader("Selecione o vídeo do produto", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    if st.button("✨ GERAR ESTRATÉGIA DE ALTA CONVERSÃO"):
        try:
            with st.spinner("🤖 O Gemini está assistindo seu vídeo..."):
                # Faz o upload para o servidor do Google
                video_file = genai.upload_file(path=tfile.name)
                
                # Monitora o processamento
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                # Prompt de Especialista
                prompt = """
                Analise este vídeo de produto como um mestre em anúncios virais (TikTok/Reels).
                Retorne:
                1. TÍTULO IMPACTANTE: 3 opções usando gatilhos de 'achadinho' e 'necessidade'.
                2. LEGENDA: Uma cópia persuasiva que foque no problema que o produto resolve.
                3. CTA: Uma chamada de ação clara para o link da bio.
                4. TAGS: 5 hashtags virais.
                5. CAPA: Indique o segundo de maior impacto visual no formato 'CAPA: X'.
                
                Seja criativo e use emojis. Não use rótulos fixos, foque no texto pronto para copiar.
                """
                
                response = model.generate_content([video_file, prompt])
                res_text = response.text
                
                st.success("✅ Conteúdo Gerado!")
                
                # Exibição do Resultado
                texto_para_copiar = "\n".join([l for l in res_text.split('\n') if "CAPA:" not in l])
                st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                st.code(texto_para_copiar, language="")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Captura da imagem da Capa sugerida
                match = re.search(r'CAPA:\s*(\d+)', res_text)
                segundo = int(match.group(1)) if match else 1
                
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                if ret:
                    st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                cap.release()
                
                # Limpa o arquivo do Google para não gastar sua cota
                genai.delete_file(video_file.name)
                
        except Exception as e:
            st.error(f"Erro na análise: {e}")

st.markdown("---")
st.caption("Dica: Certifique-se de que sua chave API no Google AI Studio tem acesso ao modelo 2.0 ou 1.5.")
