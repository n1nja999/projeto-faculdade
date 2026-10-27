"""Montagem da página: cabeçalho, filtros e navegação entre as seções."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd
import streamlit as st

from .abas import (
    aba_comparacao,
    aba_comportamento,
    aba_custo_do_erro,
    aba_limitacoes,
    aba_modelo_previsao,
    aba_pesquisa,
    aba_por_grupo,
    aba_recomendacoes,
    aba_visao_geral,
)
from .config import NOMES_MODELOS, SERVICOS, navegacao_lazy
from .dados import gerar_dados
from .estilo import aplicar_estilo
from .modelos import Resultado, treinar_modelos


@dataclass(frozen=True)
class Contexto:
    """Tudo que as seções podem precisar, calculado uma vez por execução."""

    dados: pd.DataFrame
    filtrados: pd.DataFrame
    resultado: Resultado
    servicos_escolhidos: list[str]
    modelo_escolhido: str


SECOES: dict[str, Callable[[Contexto], None]] = {
    "Visão geral": lambda c: aba_visao_geral(c.filtrados),
    "Por grupo": lambda c: aba_por_grupo(c.filtrados),
    "Comportamento": lambda c: aba_comportamento(c.filtrados),
    "Modelo de previsão": lambda c: aba_modelo_previsao(c.dados, c.resultado, c.servicos_escolhidos),
    "Pesquisa Hibou": lambda c: aba_pesquisa(c.dados),
    "Comparação de modelos": lambda c: aba_comparacao(c.resultado, c.modelo_escolhido),
    "Custo do erro": lambda c: aba_custo_do_erro(c.resultado, c.modelo_escolhido),
    "Recomendações": lambda c: aba_recomendacoes(c.filtrados),
    "Limitações": lambda c: aba_limitacoes(),
}


def main() -> None:
    st.set_page_config(
        page_title="Cancelamento de Streaming no Brasil",
        page_icon="🎬",
        layout="wide",
    )
    aplicar_estilo()

    st.markdown(
        '<div class="titulo">Quem cancela o streaming no Brasil, e por quê</div>'
        '<div class="subtitulo">Clientes simulados, com a taxa de cancelamento de cada serviço '
        "vinda da pesquisa da Hibou, feita em 2023 com 1.400 pessoas.</div>"
        '<div class="pergunta"><b>Pergunta de pesquisa:</b> quais fatores mais aumentam o risco '
        "de cancelamento de uma assinatura de streaming e é possível prever quem vai cancelar "
        "com antecedência?</div>",
        unsafe_allow_html=True,
    )

    dados = gerar_dados()
    resultado = treinar_modelos(dados)

    st.sidebar.markdown(
        '<div class="marca">Painel de cancelamento</div>'
        '<div class="marca-sub">Filtre os serviços e escolha o modelo usado nas abas de previsão.</div>',
        unsafe_allow_html=True,
    )
    servicos_escolhidos = st.sidebar.multiselect("Serviços", SERVICOS, default=SERVICOS)
    modelo_escolhido = st.sidebar.radio(
        "Modelo para a matriz de confusão e para o custo do erro", NOMES_MODELOS
    )

    filtrados = dados[dados["servico"].isin(servicos_escolhidos)]
    if filtrados.empty:
        st.warning("Escolha pelo menos um serviço.")
        st.stop()

    ctx = Contexto(dados, filtrados, resultado, servicos_escolhidos, modelo_escolhido)
    nomes = list(SECOES)
    if navegacao_lazy():
        # Renderiza só a seção escolhida: cada interação executa 1 seção, não 9.
        ativa = st.radio(
            "Seção", nomes, horizontal=True, key="secao_ativa", label_visibility="collapsed"
        )
        SECOES[ativa](ctx)
    else:
        for aba, render in zip(st.tabs(nomes), SECOES.values()):
            with aba:
                render(ctx)
