import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time
from PIL import Image

# Configuração da Página
st.set_page_config(page_title="BrendaBot Meta Expert", page_icon="💙", layout="wide")
st.title("💙 BrendaBot: Validador de Reels e Fotos (Facebook)")

# Configurar API
API_KEY = "AIzaSyCiJyxLVYVgI7EiTuQmkQGTi1nWiQn9g_8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Upload aceita Vídeo ou Imagem
uploaded_file = st.file_uploader("Suba seu Reels ou Foto para análise...", type=["mp4", "mov", "avi", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    is_video = uploaded_file.type.startswith('video')
    
    # Processamento de arquivo temporário
    suffix = '.mp4' if is_video else '.jpg'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tfile:
        tfile.write(uploaded_file.read())
        file_path = tfile.name
    
    st.info(f"🕵️ Analisando {'Reels' if is_video else 'Foto'} conforme as políticas da Meta...")
    
    try:
        # Upload para a IA
        media_file = genai.upload_file(path=file_path)
        
        while media_file.state.name == "PROCESSING":
            time.sleep(2)
            media_file = genai.get_file(media_file.name)
            
        # PROMPT ESPECIALIZADO EM POLÍTICAS DO FACEBOOK
        prompt = """
        Atue como Especialista em Monetização e Tráfego Orgânico do Facebook (Meta).
        Analise este arquivo e retorne o relatório RIGOROSAMENTE nesta ordem:

        ### 🚨 VALIDAÇÃO DE POLÍTICAS DO FACEBOOK
        1. **ORIGINALIDADE**: (Este conteúdo corre risco de ser marcado como 'Originalidade Limitada'? O Facebook pune vídeos que parecem baixados de outras redes).
        2. **RISCO DE DESMONETIZAÇÃO**: (Analise se há violência, nudez implícita, linguagem ofensiva ou temas sensíveis que bloqueiam os 'Anúncios no Reels').
        3. **POLÍTICA DE SPAM/CLICKBAIT**: (O título ou a imagem tentam enganar o usuário? O Facebook reduz o alcance de posts que forçam o 'curtir e compartilhar').

        ### 📈 POTENCIAL DE DISTRIBUIÇÃO (ALCANCE)
        4. **PROBABILIDADE DE RECOMENDAÇÃO**: (Chance de aparecer no 'Sugeridos para você' de 0 a 100%).
        5. **RETENÇÃO VISUAL**: (Para Reels: Onde o vídeo fica cansativo? Para Foto: A imagem é nítida e centralizada para o feed mobile?).

        ### ✍️ SUGESTÃO DE POSTAGEM (MÉTODO META)
        6. **LEGENDA PARA FACEBOOK**: (Legendas no FB podem ser maiores. Crie uma que gere conversas).
        7. **3 HASHTAGS ESTRATÉGICAS**: (No Facebook, menos é mais).
        8. **PERGUNTA QUE GERA COMPARTILHAMENTO**: (O algoritmo do FB prioriza o compartilhamento sobre o like).

        ### 🌍 TRADUÇÃO
        9. Legenda resumida em Inglês.

        ### 🖼️ RECOMENDAÇÃO DE CAPA (Apenas para Vídeo)
        Escreva ao final apenas: 'CAPA: X' (segundo sugerido).
        """
        
        response = model.generate_content([media_file, prompt])
        texto_ia = response.text
        
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.subheader("📋 Relatório Meta Business")
            texto_exibicao = re.sub(r'CAPA:\s*\d+', '', texto_ia)
            st.markdown(texto_exibicao)
            
            st.divider()
            st.subheader("📋 Copiar Legenda")
            st.text_area("Pronto para o Facebook:", texto_exibicao, height=300)
        
        with col2:
            if is_video:
                match = re.search(r'CAPA:\s*(\d+)', texto_ia)
                segundo = int(match.group(1)) if match else 1
                
                cap = cv2.VideoCapture(file_path)
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
                success, frame = cap.read()
                if success:
                    st.subheader("🖼️ Thumbnail para Reels")
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(frame_rgb, use_container_width=True)
                cap.release()
            else:
                st.subheader("🖼️ Preview da Foto")
                st.image(file_path, use_container_width=True)
            
            # Alerta de Política
            if any(palavra in texto_ia.upper() for palavra in ["ARRISCADO", "CRÍTICO", "DESMONETIZAÇÃO"]):
                st.error("⚠️ CUIDADO: Este post pode violar as políticas de alcance do Facebook.")
            else:
                st.success("✅ SEGURO: Conteúdo pronto para distribuição no Facebook.")

        genai.delete_file(media_file.name)
        
    except Exception as e:
        st.error(f"Erro na análise: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
