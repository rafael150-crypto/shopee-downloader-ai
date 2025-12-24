import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
from PIL import Image

# Configuração da Página para visual Premium
st.set_page_config(page_title="BrendaBot Sentinel Pro", page_icon="🛡️", layout="wide")

# Interface Estilizada (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2227; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .status-box {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        border: 2px solid #30363d;
    }
    .safe-bg { background-color: #064e3b; color: #34d399; }
    .warning-bg { background-color: #451a03; color: #fbbf24; }
    .danger-bg { background-color: #450a0a; color: #f87171; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ BrendaBot Meta Sentinel Pro")
st.subheader("Auditoria Estratégica para Facebook Reels & Fotos")

# Configurar API
API_KEY = "AIzaSyCiJyxLVYVgI7EiTuQmkQGTi1nWiQn9g_8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("📂 Arraste seu arquivo (MP4 ou Imagem)", type=["mp4", "mov", "avi", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    is_video = uploaded_file.type.startswith('video')
    suffix = '.mp4' if is_video else '.jpg'
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
        tfile.write(uploaded_file.read())
        file_path = tfile.name
    
    with st.spinner("🕵️ Cruzando dados com as políticas da Meta..."):
        try:
            media_file = genai.upload_file(path=file_path)
            while media_file.name and genai.get_file(media_file.name).state.name == "PROCESSING":
                time.sleep(2)
            
            prompt = """
            Atue como Auditor de Políticas da Meta. 
            Analise o conteúdo e retorne o relatório RIGOROSAMENTE neste formato:

            [PONTUACAO_SEGURANCA]: X (Dê uma nota de 0 a 100, onde 100 é totalmente seguro e 0 é banimento certo)
            
            # 🛑 ANÁLISE DE SEGURANÇA (POLÍTICAS)
            - **VEREDITO**: (Status: APROVADO, RISCO MODERADO ou REPROVADO)
            - **MOTIVO**: (Explique por que o conteúdo pode ser barrado ou flopar)
            - **CLICKBAIT/SPAM**: (Análise de ganchos falsos ou iscas)

            # 📈 PERFORMANCE E ENGAJAMENTO
            - **CHANCE DE VIRALIZAÇÃO**: (0 a 100%)
            - **LEGENDA META**: (Sugestão de legenda envolvente)
            - **CTA**: (Chamada para ação matadora)

            CAPA: X (segundo sugerido)
            """
            
            response = model.generate_content([media_file, prompt])
            texto_ia = response.text
            
            # Extrair Pontuação para o Indicômetro
            try:
                score = int(re.search(r'\[PONTUACAO_SEGURANCA\]:\s*(\d+)', texto_ia).group(1))
            except:
                score = 50

            # --- HEADER DE STATUS (INDICÔMETRO) ---
            st.divider()
            
            # Definindo cores e mensagens baseadas no Score
            if score >= 80:
                color, label, bg_class = "#10b981", "CONTEÚDO SEGURO", "safe-bg"
            elif score >= 50:
                color, label, bg_class = "#f59e0b", "CONTEÚDO ARRISCADO", "warning-bg"
            else:
                color, label, bg_class = "#ef4444", "ALTO RISCO DE BLOQUEIO", "danger-bg"

            st.markdown(f"""
                <div class="status-box {bg_class}">
                    <h2 style="margin:0;">{label}</h2>
                    <p style="margin:5px 0 0 0;">Pontuação de Conformidade: {score}/100</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.progress(score / 100) # Barra de progresso nativa como indicômetro

            # --- CORPO DO RELATÓRIO ---
            col1, col2 = st.columns([1.2, 0.8])
            
            with col1:
                # Limpando o texto para exibir apenas o relatório
                texto_limpo = re.sub(r'\[PONTUACAO_SEGURANCA\]:.*?\d+', '', texto_ia)
                texto_limpo = re.sub(r'CAPA:\s*\d+', '', texto_limpo)
                st.markdown(texto_limpo)
            
            with col2:
                if is_video:
                    match = re.search(r'CAPA:\s*(\d+)', texto_ia)
                    segundo = int(match.group(1)) if match else 1
                    cap = cv2.VideoCapture(file_path)
                    cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                    success, frame = cap.read()
                    if success:
                        st.subheader("🖼️ Thumbnail Estratégica")
                        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                        ret, buffer = cv2.imencode('.jpg', frame)
                        st.download_button("📥 Baixar Capa", buffer.tobytes(), "thumb.jpg", "image/jpeg")
                    cap.release()
                else:
                    st.subheader("🖼️ Preview da Imagem")
                    st.image(file_path, use_container_width=True)
                
                st.info("💡 **Dica BrendaBot:** Vídeos com bordas pretas ou marcas d'água de terceiros reduzem o alcance no Facebook em até 70%.")

            if score >= 80: st.balloons()
            genai.delete_file(media_file.name)

        except Exception as e:
            st.error(f"Erro na auditoria: {e}")
        finally:
            if os.path.exists(file_path): os.remove(file_path)
