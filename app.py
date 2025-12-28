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
    .asset-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #238636;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ BrendaBot Meta Sentinel Pro")
st.caption("Validador de Políticas e Gerador de Ativos para Facebook (Reels & Fotos)")

# Configurar API
API_KEY = "AIzaSyBPJayL5rgY25x-zkBaZ35GDNop-8VNbt0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("📂 Arraste seu Reels ou Foto aqui...", type=["mp4", "mov", "avi", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    is_video = uploaded_file.type.startswith('video')
    suffix = '.mp4' if is_video else '.jpg'
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
        tfile.write(uploaded_file.read())
        file_path = tfile.name
    
    with st.spinner("🕵️ Auditando políticas e preparando ativos..."):
        try:
            media_file = genai.upload_file(path=file_path)
            while media_file.name and genai.get_file(media_file.name).state.name == "PROCESSING":
                time.sleep(2)
            
            prompt = """
            Atue como Auditor de Políticas da Meta e Estrategista de Viralização. 
            Analise o conteúdo e retorne o relatório RIGOROSAMENTE neste formato:

            [PONTUACAO_SEGURANCA]: X (Nota de 0 a 100 para conformidade com as regras do Facebook)
            
            # 🚨 ANÁLISE DE SEGURANÇA E POLÍTICAS
            - **VEREDITO**: (Status: APROVADO, RISCO MODERADO ou REPROVADO)
            - **CHANCE DE DAR ERRADO**: (Porcentagem e motivo principal)
            - **RISCO DE SHADOWBAN**: (Análise de conteúdo reutilizado ou sensível)

            # ✍️ ATIVOS DE POSTAGEM (CASO DECIDA POSTAR)
            - **LEGENDA PARA FACEBOOK**: (Legenda envolvente focada em compartilhamentos)
            - **HASHTAGS ESTRATÉGICAS**: (3 hashtags relevantes)
            - **CTA (CHAMADA PARA AÇÃO)**: (Pergunta para gerar comentários)
            - **QUOTES MAGNÉTICAS**: (2 frases de impacto do conteúdo)

            # 📈 ESTRATÉGIA ADICIONAL
            - **MELHOR HORÁRIO**: (Sugestão baseada no tipo de conteúdo)
            - **CAPÍTULOS/CORTES**: (Apenas se for vídeo)

            CAPA: X (segundo sugerido)
            """
            
            response = model.generate_content([media_file, prompt])
            texto_ia = response.text
            
            # Extrair Pontuação
            try:
                score = int(re.search(r'\[PONTUACAO_SEGURANCA\]:\s*(\d+)', texto_ia).group(1))
            except:
                score = 50

            # --- HEADER DE STATUS ---
            if score >= 80:
                label, bg_class = "✅ CONTEÚDO SEGURO", "safe-bg"
            elif score >= 50:
                label, bg_class = "⚠️ RISCO MODERADO", "warning-bg"
            else:
                label, bg_class = "❌ ALTO RISCO / REPROVADO", "danger-bg"

            st.markdown(f'<div class="status-box {bg_class}"><h2>{label}</h2><p>Confidência do Algoritmo: {score}/100</p></div>', unsafe_allow_html=True)
            st.progress(score / 100)

            # --- CORPO DO RELATÓRIO ---
            col1, col2 = st.columns([1.2, 0.8])
            
            with col1:
                st.subheader("📝 Relatório de Auditoria")
                # Limpando tags internas para exibição
                texto_limpo = re.sub(r'\[PONTUACAO_SEGURANCA\]:.*?\d+', '', texto_ia)
                texto_limpo = re.sub(r'CAPA:\s*\d+', '', texto_limpo)
                
                # Separar a parte de Ativos para dar destaque
                partes = texto_limpo.split('# ✍️ ATIVOS DE POSTAGEM')
                
                st.markdown(partes[0]) # Mostra a segurança primeiro
                
                if len(partes) > 1:
                    st.markdown('<div class="asset-card">', unsafe_allow_html=True)
                    st.subheader("🎯 Ativos de Postagem")
                    st.markdown(partes[1])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📋 Área de Cópia Rápida")
                    st.text_area("Copie a legenda e ativos aqui:", partes[1].strip(), height=250)
            
            with col2:
                if is_video:
                    match = re.search(r'CAPA:\s*(\d+)', texto_ia)
                    segundo = int(match.group(1)) if match else 1
                    cap = cv2.VideoCapture(file_path)
                    cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                    success, frame = cap.read()
                    if success:
                        st.subheader("🖼️ Thumbnail Sugerida")
                        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
                        ret, buffer = cv2.imencode('.jpg', frame)
                        st.download_button("📥 Baixar Capa", buffer.tobytes(), "thumb_meta.jpg", "image/jpeg")
                    cap.release()
                else:
                    st.subheader("🖼️ Preview do Post")
                    st.image(file_path, use_container_width=True)

            if score >= 80: st.balloons()
            genai.delete_file(media_file.name)

        except Exception as e:
            st.error(f"Erro na auditoria: {e}")
        finally:
            if os.path.exists(file_path): os.remove(file_path)
