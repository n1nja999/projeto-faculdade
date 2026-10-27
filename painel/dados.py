from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from .config import DISTRIBUICOES, N_CLIENTES, REGRAS, SEMENTE, TAXA_BASE


def simular_clientes(n: int = N_CLIENTES, semente: int = SEMENTE) -> pd.DataFrame:
    rng = np.random.default_rng(semente)

    dados = pd.DataFrame(
        {col: rng.choice(opcoes, n, p=probs) for col, (opcoes, probs) in DISTRIBUICOES.items()}
    )
    dados["meses_assinatura"] = rng.integers(1, 60, n)
    dados["horas_mes"] = rng.gamma(2.0, 8.0, n).round(1)
    dados["dias_sem_acessar"] = rng.integers(0, 60, n)

    chance = dados["servico"].map(TAXA_BASE).to_numpy()
    for regra in REGRAS:
        chance = chance * np.where(regra.condicao(dados), regra.multiplicador, 1.0)
    chance = np.clip(chance, 0.0, 0.95)

    dados["cancelou"] = (rng.random(n) < chance).astype(int)
    return dados


@st.cache_data(show_spinner="Gerando clientes simulados...")
def gerar_dados() -> pd.DataFrame:
    return simular_clientes()
