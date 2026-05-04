"""
🚀 Prospecção Inteligente - App de busca de clientes via Google Maps
"""

import streamlit as st
import pandas as pd
import urllib.parse
import re
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# ── Configuração da página ──
st.set_page_config(
    page_title="Prospecção Inteligente",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Premium ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ═══════════════════════════════════════════
   BASE & RESET
   ═══════════════════════════════════════════ */
*, *::before, *::after { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
html { scroll-behavior: smooth; }

.stApp {
    background-color: #0b0f19;
    background-image: url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.main .block-container {
    padding: 1.5rem 2rem 3rem;
    max-width: 1280px;
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    margin-top: 2rem;
    box-shadow: 0 10px 50px rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.05);
}

/* Esconder o header padrão do Streamlit */
header[data-testid="stHeader"] { background: transparent !important; }

/* ═══════════════════════════════════════════
   ANIMATED HERO HEADER
   ═══════════════════════════════════════════ */
.hero-header {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #6C63FF);
    background-size: 400% 400%;
    animation: gradientShift 12s ease infinite;
    padding: 3rem 2.5rem 2.5rem;
    border-radius: 24px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 25px 80px rgba(108, 99, 255, 0.25), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.hero-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(circle at 20% 50%, rgba(108,99,255,0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(6,182,212,0.1) 0%, transparent 40%),
        radial-gradient(circle at 50% 80%, rgba(59,130,246,0.08) 0%, transparent 40%);
    pointer-events: none;
}
.hero-header::after {
    content: '';
    position: absolute;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(108,99,255,0.2), transparent 70%);
    top: -100px; right: -80px;
    border-radius: 50%;
    animation: float 6s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-20px, 15px); }
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(255,255,255,0.8);
    margin-bottom: 1rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    position: relative;
}
.hero-header h1 {
    color: white;
    font-size: 2.6rem;
    font-weight: 900;
    margin: 0 0 0.5rem;
    position: relative;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.hero-header h1 span {
    background: linear-gradient(135deg, #a78bfa, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-header p {
    color: rgba(255,255,255,0.6);
    font-size: 1rem;
    font-weight: 400;
    margin: 0;
    position: relative;
}

/* ═══════════════════════════════════════════
   GLASSMORPHISM RESULT CARDS
   ═══════════════════════════════════════════ */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1rem;
}
.result-card {
    background: rgba(22, 27, 45, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(108, 99, 255, 0.12);
    border-radius: 20px;
    padding: 1.6rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6C63FF, #06B6D4, #a78bfa);
    opacity: 0;
    transition: opacity 0.4s ease;
}
.result-card:hover {
    border-color: rgba(108, 99, 255, 0.35);
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(108, 99, 255, 0.12);
}
.result-card:hover::before { opacity: 1; }

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    gap: 12px;
}
.card-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #F1F5F9;
    line-height: 1.3;
    flex: 1;
}
.card-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(108,99,255,0.2), transparent);
    margin: 0.8rem 0;
}
.card-detail {
    font-size: 0.82rem;
    color: #8892B0;
    margin: 6px 0;
    display: flex;
    align-items: center;
    gap: 10px;
    line-height: 1.4;
}
.card-detail .icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(108,99,255,0.1);
    border-radius: 8px;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.card-rating {
    color: #FBBF24;
    font-weight: 600;
}
.card-actions {
    display: flex;
    gap: 8px;
    margin-top: 1.1rem;
    flex-wrap: wrap;
}

/* ═══════════════════════════════════════════
   WHATSAPP BUTTON
   ═══════════════════════════════════════════ */
.whatsapp-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #25D366, #128C7E);
    color: white !important;
    padding: 10px 22px;
    border-radius: 14px;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 0.82rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.25);
    letter-spacing: 0.2px;
}
.whatsapp-btn:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 25px rgba(37, 211, 102, 0.35);
    filter: brightness(1.1);
}
.site-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(108,99,255,0.12);
    color: #a78bfa !important;
    padding: 10px 18px;
    border-radius: 14px;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 0.82rem;
    border: 1px solid rgba(108,99,255,0.2);
    transition: all 0.3s ease;
}
.site-btn:hover {
    background: rgba(108,99,255,0.2);
    border-color: rgba(108,99,255,0.4);
    transform: translateY(-1px);
}

/* ═══════════════════════════════════════════
   STATUS BADGES
   ═══════════════════════════════════════════ */
.status-badge {
    padding: 4px 14px;
    border-radius: 50px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    white-space: nowrap;
    text-transform: uppercase;
}
.status-novo { background: rgba(108,99,255,0.15); color: #a78bfa; border: 1px solid rgba(108,99,255,0.3); }
.status-negociacao { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.status-finalizado { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.status-descartado { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

/* ═══════════════════════════════════════════
   METRIC CARDS
   ═══════════════════════════════════════════ */
.metric-card {
    background: rgba(22, 27, 45, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(108, 99, 255, 0.1);
    border-radius: 18px;
    padding: 1.4rem 1rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 20%; right: 20%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #6C63FF, transparent);
    opacity: 0.4;
}
.metric-card:hover { transform: translateY(-2px); border-color: rgba(108,99,255,0.25); }
.metric-icon { font-size: 1.5rem; margin-bottom: 0.4rem; }
.metric-value {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #a78bfa, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.72rem;
    color: #64748B;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ═══════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0d14, #111629) !important;
    border-right: 1px solid rgba(108,99,255,0.08) !important;
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: #64748B !important;
    font-weight: 700 !important;
}
.sidebar-brand {
    text-align: center;
    padding: 1rem 0 0.5rem;
    margin-bottom: 0.5rem;
}
.sidebar-brand .logo { font-size: 2rem; margin-bottom: 0.3rem; }
.sidebar-brand .name {
    font-size: 1rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-brand .tagline { font-size: 0.7rem; color: #475569; font-weight: 400; }

/* ═══════════════════════════════════════════
   INPUTS & BUTTONS
   ═══════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 14px !important;
    border: 1px solid rgba(108, 99, 255, 0.15) !important;
    background: rgba(15, 18, 30, 0.6) !important;
    font-size: 0.88rem !important;
    padding: 0.7rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.12) !important;
}
.stSelectbox > div > div { border-radius: 14px !important; }

.stButton > button {
    border-radius: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 0.6rem 1.5rem !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF, #4F46E5) !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(108,99,255,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(108,99,255,0.4) !important;
    filter: brightness(1.1) !important;
}
.stDownloadButton > button {
    border-radius: 14px !important;
    font-weight: 600 !important;
    border: 1px solid rgba(108,99,255,0.2) !important;
    background: rgba(108,99,255,0.08) !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(108,99,255,0.15) !important;
    border-color: rgba(108,99,255,0.4) !important;
    transform: translateY(-1px) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* ═══════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    animation: fadeInUp 0.8s ease;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.empty-icon {
    width: 100px; height: 100px;
    margin: 0 auto 1.5rem;
    background: rgba(108,99,255,0.08);
    border-radius: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    border: 1px solid rgba(108,99,255,0.12);
    animation: pulse-icon 3s ease-in-out infinite;
}
@keyframes pulse-icon {
    0%, 100% { box-shadow: 0 0 0 0 rgba(108,99,255,0.15); }
    50% { box-shadow: 0 0 0 15px rgba(108,99,255,0); }
}
.empty-state h3 { color: #CBD5E1; font-weight: 700; font-size: 1.3rem; margin-bottom: 0.5rem; }
.empty-state p { color: #475569; max-width: 420px; margin: 0 auto; font-size: 0.9rem; line-height: 1.6; }

/* Section titles */
.section-title {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #475569;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(108,99,255,0.2), transparent);
}

/* Footer */
.app-footer {
    text-align: center;
    padding: 2rem 0 1rem;
    color: #334155;
    font-size: 0.75rem;
    font-weight: 500;
}
.app-footer a { color: #6C63FF; text-decoration: none; }

/* ═══════════════════════════════════════════
   LOGIN SCREEN
   ═══════════════════════════════════════════ */
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    animation: fadeInUp 0.8s ease;
}
.login-card {
    background: rgba(22, 27, 45, 0.8);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(108, 99, 255, 0.15);
    border-radius: 28px;
    padding: 3rem 2.5rem;
    max-width: 440px;
    width: 100%;
    text-align: center;
    box-shadow: 0 25px 80px rgba(0,0,0,0.3), 0 0 120px rgba(108,99,255,0.08);
    position: relative;
    overflow: hidden;
}
.login-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #6C63FF, #06B6D4, #a78bfa);
}
.login-logo { font-size: 3.5rem; margin-bottom: 1rem; }
.login-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #F1F5F9;
    margin-bottom: 0.3rem;
}
.login-subtitle {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 2rem;
    line-height: 1.5;
}
.login-footer {
    margin-top: 1.5rem;
    font-size: 0.75rem;
    color: #475569;
}
.login-footer a {
    color: #6C63FF;
    text-decoration: none;
    font-weight: 600;
}
.plan-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.2);
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #a78bfa;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ── Funções utilitárias ──
def limpar_numero(telefone: str) -> str:
    num = re.sub(r"\D", "", str(telefone))
    if not num:
        return ""
    if not num.startswith("55") and len(num) >= 10:
        num = "55" + num
    return num


MODELOS_MENSAGEM = {
    "🤝 Comercial Direta": (
        "Olá, vi que a {nome} é referência em {segmento} aqui na região. "
        "Gostaria de saber quem é o responsável pelas parcerias/compras "
        "para apresentarmos uma solução. Podemos falar?"
    ),
    "💬 Consultiva / Suave": (
        "Oi! Tudo bem? Encontrei o contato de vocês e fiquei interessado "
        "nos serviços da {nome}. Vocês atendem pelo WhatsApp para tirar "
        "algumas dúvidas?"
    ),
    "🌐 Networking": (
        "Olá! Sou do setor de {segmento} e estou expandindo meus contatos "
        "com empresas da área. Gostaria de enviar nosso catálogo para a "
        "{nome}. Qual o melhor e-mail ou contato?"
    ),
    "✏️ Personalizada": "",
}

DATA_FILE = "dados_prospeccao.json"


def salvar_dados(dados: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_dados() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def gerar_link_whatsapp(telefone, nome_empresa, segmento, modelo, msg_custom=""):
    numero = limpar_numero(telefone)
    if not numero:
        return ""
    if modelo == "✏️ Personalizada" and msg_custom:
        try:
            mensagem = msg_custom.format(nome=nome_empresa, segmento=segmento)
        except (KeyError, IndexError):
            mensagem = msg_custom
    elif modelo in MODELOS_MENSAGEM:
        mensagem = MODELOS_MENSAGEM[modelo].format(nome=nome_empresa, segmento=segmento)
    else:
        mensagem = f"Olá, {nome_empresa}!"
    return f"https://wa.me/{numero}?text={urllib.parse.quote(mensagem)}"


# ── Inicializar estado ──
if "resultados" not in st.session_state:
    st.session_state.resultados = carregar_dados()
if "busca_realizada" not in st.session_state:
    st.session_state.busca_realizada = False
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ── Efeito de Mouse Trail (Partículas) ──
st.markdown("""<img src onerror="const doc=window.document;if(!doc.getElementById('mouse-trail-style')){const style=doc.createElement('style');style.id='mouse-trail-style';style.innerHTML='.mouse-particle{position:fixed;width:10px;height:10px;background:radial-gradient(circle,#06B6D4 0%,#6C63FF 100%);border-radius:50%;pointer-events:none;z-index:999999;opacity:0.9;box-shadow:0 0 10px #6C63FF,0 0 20px #06B6D4;transition:transform 0.6s cubic-bezier(0.1,0.8,0.3,1),opacity 0.6s ease-out;}';doc.head.appendChild(style);doc.addEventListener('mousemove',function(e){if(Math.random()>0.4)return;const p=doc.createElement('div');p.className='mouse-particle';p.style.left=(e.clientX-5)+'px';p.style.top=(e.clientY-5)+'px';p.style.transform='scale(1)';doc.body.appendChild(p);p.getBoundingClientRect();p.style.transform='translate('+(Math.random()*40-20)+'px,'+(Math.random()*40-20)+'px) scale(0)';p.style.opacity='0';setTimeout(()=>{p.remove();},600);});}" style="display:none;">""", unsafe_allow_html=True)

# ── Autenticação (Gate) ──
# Tenta carregar senhas ocultas da nuvem (Streamlit Secrets)
try:
    chaves_validas = st.secrets["chaves_clientes"]
except Exception:
    # Se não houver segredos configurados, usa esta lista padrão:
    chaves_validas = [
        "CLIENTE2024",
        "VIP2025",
        "TESTE123",
        "JOAO_ACADEMIA"
    ]

if not st.session_state.autenticado:
    _, col2, _ = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 10vh; padding: 2rem; background: rgba(22, 27, 45, 0.8); backdrop-filter: blur(24px); border-radius: 28px; border: 1px solid rgba(108, 99, 255, 0.15); box-shadow: 0 25px 80px rgba(0,0,0,0.3);">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">🚀</div>
            <h1 style="font-size: 1.8rem; font-weight: 800; color: #F1F5F9; margin-bottom: 0.5rem;">ProspectAI</h1>
            <p style="color: #64748B; margin-bottom: 2rem; font-size: 0.9rem;">Área restrita. Informe sua chave de acesso para utilizar a ferramenta de prospecção.</p>
        """, unsafe_allow_html=True)
        
        chave = st.text_input("Chave de Acesso", type="password", placeholder="Sua chave secreta", label_visibility="collapsed")
        
        if st.button("Acessar Sistema", use_container_width=True, type="primary"):
            if chave in chaves_validas:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Chave de acesso inválida!")
                
        st.markdown("""
            <div style="margin-top: 1.5rem; font-size: 0.75rem; color: #475569;">
                Não tem uma chave? <a href="#" style="color: #6C63FF; font-weight: 600; text-decoration: none;">Fale conosco</a>
                <br>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(108,99,255,0.1); border: 1px solid rgba(108,99,255,0.2); padding: 6px 16px; border-radius: 50px; font-size: 0.72rem; font-weight: 600; color: #a78bfa; margin-top: 1rem;">💎 Plano Pro</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.stop()


# ── Header ──
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">⚡ Desenvolvido por meio de Web Scraping</div>
    <h1>Prospecção <span>Inteligente</span></h1>
    <p>Encontre novos clientes automaticamente via Google Maps</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ──
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="logo">🚀</div><div class="name">ProspectAI</div><div class="tagline">Geração de Leads Inteligente</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("⚙️ Configurações Avançadas (n8n)"):
        webhook_url = st.text_input("Webhook URL (n8n)", value="", placeholder="https://seu-n8n.com/webhook/...")
        st.caption("Insira a URL do webhook do n8n para realizar as buscas via API externa em vez de scraping local.")

    st.markdown("---")

    st.markdown("### 🔍 Busca")
    segmento = st.text_input("Segmento", placeholder="Ex: Academias, Restaurantes...")
    localizacao = st.text_input("Localização", placeholder="Ex: Porto Alegre - RS")
    max_results = st.slider("Máx. resultados", 5, 40, 15)
    buscar_emails = st.checkbox("🔎 Buscar e-mails nos sites", value=False,
                                 help="Visita o site de cada empresa para extrair e-mails. Mais lento.")

    st.markdown("---")
    st.markdown("### 💬 Mensagem WhatsApp")
    modelo_msg = st.selectbox("Modelo de mensagem", list(MODELOS_MENSAGEM.keys()))
    mensagem_custom = ""
    if modelo_msg == "✏️ Personalizada":
        mensagem_custom = st.text_area(
            "Sua mensagem",
            placeholder="Use {nome} e {segmento} como variáveis.\nEx: Olá {nome}, vi que vocês atuam em {segmento}...",
            height=100,
        )

    st.markdown("---")
    st.markdown("### 📊 Filtros")
    filtro_status = st.multiselect(
        "Filtrar por status",
        ["🆕 Novo", "📞 Em negociação", "✅ Finalizado", "❌ Descartado"],
        default=["🆕 Novo", "📞 Em negociação", "✅ Finalizado", "❌ Descartado"],
    )

    st.markdown("---")
    buscar = st.button("🔍 Buscar Clientes", use_container_width=True, type="primary")


# ── Execução da busca ──
if buscar and segmento and localizacao:
    with st.spinner("🔄 Processando busca... Isso pode levar alguns segundos."):
        try:
            if webhook_url:
                # ── Busca via Webhook (n8n) ──
                import requests
                
                payload = {
                    "segmento": segmento,
                    "localizacao": localizacao,
                    "max_resultados": max_results,
                    "buscar_emails": buscar_emails
                }
                
                response = requests.post(webhook_url, json=payload, timeout=120)
                
                if response.status_code == 200:
                    resultados = response.json()
                    # Caso o n8n retorne os resultados dentro de uma chave específica, ex: {"data": [...]}
                    if isinstance(resultados, dict) and "data" in resultados:
                        resultados = resultados["data"]
                else:
                    st.error(f"❌ Erro na API do n8n (Status {response.status_code}): {response.text}")
                    resultados = []
                    
            else:
                # ── Busca Local (Selenium) ──
                progress_bar = st.progress(0, text="Iniciando scraping local...")
                from scraper import buscar_empresas

                def atualizar_progresso(atual, total):
                    progress_bar.progress(atual / total, text=f"Extraindo {atual}/{total}...")

                resultados = buscar_empresas(
                    segmento=segmento,
                    localizacao=localizacao,
                    max_resultados=max_results,
                    buscar_emails=buscar_emails,
                    progress_callback=atualizar_progresso,
                )
                progress_bar.progress(1.0, text="✅ Busca concluída!")

            if resultados:
                st.session_state.resultados = resultados
                st.session_state.busca_realizada = True
                st.session_state.segmento_atual = segmento
                salvar_dados(resultados)
                st.success(f"✅ {len(resultados)} empresas encontradas!")
            else:
                st.warning("Nenhum resultado retornado. Tente outro segmento ou verifique sua configuração.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Falha de conexão com o Webhook: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro na busca: {str(e)}")

elif buscar:
    st.warning("⚠️ Preencha o segmento e a localização para buscar.")


# ── Métricas ──
dados = st.session_state.resultados
if dados:
    col1, col2, col3, col4 = st.columns(4)
    total = len(dados)
    novos = sum(1 for d in dados if d.get("Status") == "🆕 Novo")
    negociando = sum(1 for d in dados if d.get("Status") == "📞 Em negociação")
    finalizados = sum(1 for d in dados if d.get("Status") == "✅ Finalizado")

    for col, valor, label, icon in [
        (col1, total, "Total", "📋"),
        (col2, novos, "Novos", "✨"),
        (col3, negociando, "Negociação", "🤝"),
        (col4, finalizados, "Fechados", "🏆"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{valor}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


# ── Exibição dos resultados ──
if dados:
    # Filtrar por status
    dados_filtrados = [d for d in dados if d.get("Status", "🆕 Novo") in filtro_status]

    if not dados_filtrados:
        st.info("Nenhum resultado com os filtros selecionados.")
    else:
        seg_atual = st.session_state.get("segmento_atual", segmento or "")

        # Tabs: Cards vs Tabela
        tab_cards, tab_tabela = st.tabs(["📇 Cards", "📊 Tabela"])

        with tab_cards:
            for i, empresa in enumerate(dados_filtrados):
                nome = empresa.get("Nome", "—")
                tel = empresa.get("Telefone", "—")
                end = empresa.get("Endereço", "—")
                site = empresa.get("Site", "—")
                rating = empresa.get("Avaliação", "—")
                email = empresa.get("E-mail", "—")
                status = empresa.get("Status", "🆕 Novo")

                link_wpp = gerar_link_whatsapp(tel, nome, seg_atual, modelo_msg, mensagem_custom)

                # Card HTML
                status_class = {
                    "🆕 Novo": "status-novo",
                    "📞 Em negociação": "status-negociacao",
                    "✅ Finalizado": "status-finalizado",
                    "❌ Descartado": "status-descartado",
                }.get(status, "status-novo")

                wpp_html = (
                    f'<a href="{link_wpp}" target="_blank" class="whatsapp-btn">📱 Chamar no WhatsApp</a>'
                    if link_wpp else '<span style="color:#555;font-size:0.8rem;">Sem telefone</span>'
                )

                st.markdown(f"""
                <div class="result-card">
                    <div class="card-header">
                        <div class="card-name">{nome}</div>
                        <span class="status-badge {status_class}">{status}</span>
                    </div>
                    <div class="card-divider"></div>
                    <div class="card-detail"><span class="icon">📞</span> {tel}</div>
                    <div class="card-detail"><span class="icon">📍</span> {end}</div>
                    <div class="card-detail"><span class="icon">📧</span> {email}</div>
                    <div class="card-detail card-rating"><span class="icon">⭐</span> {rating}</div>
                    <div class="card-actions">
                        {wpp_html}
                        {f'<a href="{"https://" + site if not site.startswith("http") else site}" target="_blank" class="site-btn">🌐 Site</a>' if site not in ('—', '', 'N/A') else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Status selector
                col_status, col_space = st.columns([1, 3])
                with col_status:
                    novo_status = st.selectbox(
                        "Status",
                        ["🆕 Novo", "📞 Em negociação", "✅ Finalizado", "❌ Descartado"],
                        index=["🆕 Novo", "📞 Em negociação", "✅ Finalizado", "❌ Descartado"].index(status),
                        key=f"status_{i}",
                        label_visibility="collapsed",
                    )
                    if novo_status != status:
                        # Atualizar no session_state
                        idx_real = dados.index(empresa)
                        st.session_state.resultados[idx_real]["Status"] = novo_status
                        salvar_dados(st.session_state.resultados)
                        st.rerun()

        with tab_tabela:
            df = pd.DataFrame(dados_filtrados)
            # Adicionar coluna de link WhatsApp
            df["Link WhatsApp"] = df.apply(
                lambda row: gerar_link_whatsapp(
                    row.get("Telefone", ""), row.get("Nome", ""),
                    seg_atual, modelo_msg, mensagem_custom
                ), axis=1
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Exportação ──
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 Exportar dados</div>', unsafe_allow_html=True)
    col_csv, col_excel = st.columns(2)

    df_export = pd.DataFrame(dados)
    seg_atual = st.session_state.get("segmento_atual", segmento or "")
    df_export["Link WhatsApp"] = df_export.apply(
        lambda row: gerar_link_whatsapp(
            row.get("Telefone", ""), row.get("Nome", ""),
            seg_atual, modelo_msg, mensagem_custom
        ), axis=1
    )

    with col_csv:
        csv = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📄 Baixar CSV",
            csv,
            f"prospeccao_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            use_container_width=True,
        )
    with col_excel:
        try:
            from io import BytesIO
            buffer = BytesIO()
            df_export.to_excel(buffer, index=False, engine="openpyxl")
            st.download_button(
                "📊 Baixar Excel",
                buffer.getvalue(),
                f"prospeccao_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except ImportError:
            st.info("Instale openpyxl para exportar em Excel.")

else:
    # Estado vazio – instrução
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>Pronto para prospectar!</h3>
        <p>
            Preencha o <strong>segmento</strong> e a <strong>localização</strong> na barra lateral
            e clique em <strong>Buscar Clientes</strong> para começar.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ──
st.markdown(
    f'<div class="app-footer">'
    f'🚀 <strong>ProspectAI</strong> &nbsp;·&nbsp; Prospecção Inteligente &nbsp;·&nbsp; {datetime.now().strftime("%Y")}'
    f'</div>',
    unsafe_allow_html=True,
)
