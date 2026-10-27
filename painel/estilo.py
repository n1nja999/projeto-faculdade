from __future__ import annotations
from html import escape
import streamlit as st

COR_FUNDO = "#121316"
COR_SUPERFICIE = "#1B1D22"
COR_LINHA = "#2A2D35"
COR_TEXTO = "#ECE9E2"
COR_MUDO = "#9A9AA3"
COR_DESTAQUE = "#F2B84B"
COR_NEUTRA = "#59606E"
COR_APOIO = "#6C8CD5"
COR_CANCELOU = "#E5484D"
COR_CONTINUOU = "#4CC38A"

CORES_SERVICO = {
    "Netflix": "#E50914",
    "HBO Max": "#8B5CF6",
    "Prime Video": "#38BDF8",
    "Disney+": "#3B5BFF",
    "Paramount+": "#14B8A6",
    "Globoplay": "#F59E0B",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Instrument+Sans:wght@400;500;600&display=swap');

html, body, .stApp, .stMarkdown, p, label, li, button, input, textarea {{
    font-family: 'Instrument Sans', system-ui, sans-serif;
}}
.stApp {{ background: {COR_FUNDO}; }}
.block-container {{ padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1240px; }}
header[data-testid="stHeader"] {{ background: transparent; }}
footer, #MainMenu, .stAppDeployButton {{ display: none !important; }}

.titulo {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(1.9rem, 3.4vw, 2.8rem);
    line-height: 1.08;
    letter-spacing: -0.02em;
    color: {COR_TEXTO};
    margin: 0 0 0.6rem 0;
    max-width: 22ch;
}}
.subtitulo {{
    color: {COR_MUDO};
    font-size: 1.02rem;
    line-height: 1.55;
    max-width: 68ch;
    margin: 0 0 1.4rem 0;
}}
.pergunta {{
    border-left: 3px solid {COR_DESTAQUE};
    background: {COR_SUPERFICIE};
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    color: {COR_TEXTO};
    line-height: 1.5;
    max-width: 80ch;
    margin-bottom: 1.8rem;
}}
.pergunta b {{ color: {COR_DESTAQUE}; font-weight: 600; }}

.secao {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: {COR_TEXTO};
    margin: 1.6rem 0 0.6rem 0;
}}
.insight {{
    border-left: 3px solid {COR_LINHA};
    padding: 4px 0 4px 14px;
    color: {COR_MUDO};
    line-height: 1.5;
    margin: 0.6rem 0 1rem 0;
}}
.insight b {{ color: {COR_TEXTO}; font-weight: 600; }}

.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {COR_LINHA}; }}
.stTabs [data-baseweb="tab"] {{
    height: 46px;
    padding: 0 14px;
    color: {COR_MUDO};
    font-weight: 500;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {COR_TEXTO}; }}
.stTabs [aria-selected="true"] {{ color: {COR_TEXTO}; font-weight: 600; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {COR_DESTAQUE}; height: 3px; }}

[data-testid="stMetric"] {{
    background: {COR_SUPERFICIE};
    border: 1px solid {COR_LINHA};
    border-radius: 10px;
    padding: 16px 18px;
}}
[data-testid="stMetricLabel"] p {{ color: {COR_MUDO}; font-size: 0.9rem; }}
[data-testid="stMetricValue"] {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    letter-spacing: -0.01em;
}}

[data-testid="stSidebar"] {{ background: {COR_SUPERFICIE}; border-right: 1px solid {COR_LINHA}; }}
.marca {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: {COR_TEXTO};
    margin-bottom: 0.2rem;
}}
.marca-sub {{ color: {COR_MUDO}; font-size: 0.85rem; margin-bottom: 1.4rem; line-height: 1.4; }}
.stMultiSelect span[data-baseweb="tag"] {{
    background: {COR_LINHA};
    color: {COR_TEXTO};
    border-radius: 6px;
}}

[data-testid="stDataFrame"] {{ border: 1px solid {COR_LINHA}; border-radius: 10px; overflow: hidden; }}
[data-testid="stAlert"] {{ border-radius: 10px; }}
[data-testid="stCaptionContainer"] {{ color: {COR_MUDO}; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 10px; }}
</style>
"""

def aplicar_estilo() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
def secao(texto: str) -> None:
    st.markdown(f'<div class="secao">{escape(texto)}</div>', unsafe_allow_html=True)
def negrito(valor: object) -> str:
    return f"<b>{escape(str(valor))}</b>"
def insight(html_seguro: str) -> None:
    st.markdown(f'<div class="insight">{html_seguro}</div>', unsafe_allow_html=True)
def pct(v: float) -> str:
    return f"{v:.1f}%"
def numero(v: float) -> str:
    return f"{v:.1f}"
def inteiro_br(v: int) -> str:
    return f"{v:,}".replace(",", ".")
def brl(valor: float) -> str:
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {abs(valor):,.0f}".replace(",", ".")
