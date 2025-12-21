import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="Estrategista de Achadinhos AI", page_icon="📈")

# Estilo focado em conversão
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { 
        width: 100%; 
        border-radius: 25px; 
        height: 3.5em; 
        background-color: #EE4D2D; 
        color: white; 
        font-weight: bold;
        font-size: 1.1em;
        border: none;
    }
    .strategy-card { 
        background-color: #f9f9f9; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #eeeeee;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Estrategista de Vendas AI")
st.write("Analise seu vídeo e gere títulos, legendas e capas que convertem em vendas.")

# 1. CONFIGURAÇÃO DA API
# Substitua pela sua chave real
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)

# Ajuste do modelo para evitar o erro 404
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. UPLOAD DO VÍDEO
st.markdown("### 📽️ Passo 1: Carregar Vídeo")
uploaded_file = st.file_uploader("Selecione o vídeo (sem marca d'água)", type=["mp4", "mov", "avi"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.video(tfile.name)
    
    st.markdown("---")
    st.markdown("### 🤖 Passo 2: Gerar Conteúdo")
    
    if st.button("✨ CRIAR ESTRATÉGIA VIRAL"):
        try:
            with st.spinner("🤖 Analisando o produto e criando os textos..."):
                # Enviar vídeo para o Gemini
                video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
                
                # Aguardar o processamento do vídeo pelo Google
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                if video_file.state.name == "FAILED":
                    st.error("Erro no processamento do vídeo pelo Google. Tente novamente.")
                    st.stop()

                prompt = """
                Atue como um Copywriter especialista em TikTok e YouTube Shorts para afiliados da Shopee.
                Analise o vídeo do produto e forneça:
                
                1. TRÊS OPÇÕES DE TÍTULOS (com gatilhos de curiosidade, escassez ou urgência).
                2. LEGENDA PERSUASIVA (focada no benefício principal e chamada para ação).
                3. 5 HASHTAGS (específicas para o nicho do produto).
                4. MELHOR SEGUNDO PARA CAPA: Indique o segundo exato e escreva apenas 'CAPA: X'.
                
                NÃO use as palavras 'Títulos:', 'Legenda:' ou 'Hashtags:'. Use emojis.
                """
                
                response = model.generate_content([video_file, prompt])
                res_text = response.text
                
                # Exibição dos Resultados
                st.success("✅ Estratégia criada!")
                
                # Separar o texto da capa
                texto_para_copiar = "\n".join([l for l in res_text.split('\n') if "CAPA:" not in l])
                
                st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                st.subheader("📝 Copie e Cole")
                st.code(texto_para_copiar, language="")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Processar a imagem da Capa
                match = re.search(r'CAPA:\s*(\d+)', res_text)
                segundo = int(match.group(1)) if match else 1
                
                cap = cv2.VideoCapture(tfile.name)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                ret, frame = cap.read()
                
                if ret:
                    st.markdown("### 🖼️ Sugestão de Capa")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                    st.caption(f"Cena sugerida no segundo {segundo}.")
                cap.release()
                
                # Deletar arquivo do servidor do Google para economizar espaço
                genai.delete_file(video_file.name)
                
        except Exception as e:
            st.error(f"Erro na análise: {e}")

st.markdown("---")
st.caption("Dica: Use vídeos limpos para que a IA identifique melhor o produto.")
