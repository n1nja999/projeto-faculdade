from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

import pandas as pd


def navegacao_lazy() -> bool:
    return os.environ.get("PAINEL_NAVEGACAO", "abas").lower() == "lazy"

SEMENTE = 42
N_CLIENTES = 10_000
LIMIAR_MIN, LIMIAR_MAX, LIMIAR_PASSO, LIMIAR_PADRAO = 0.05, 0.90, 0.05, 0.30

SERVICOS = ["Netflix", "HBO Max", "Prime Video", "Disney+", "Paramount+", "Globoplay"]

TAXA_2022 = {"Netflix": 40, "Prime Video": 23, "Globoplay": 24, "Disney+": 14, "HBO Max": 13}
TAXA_2023 = {"Netflix": 33, "Prime Video": 28, "Globoplay": 27, "Disney+": 17, "HBO Max": 13}

TAXA_BASE = {servico: taxa / 100 for servico, taxa in TAXA_2023.items()}
TAXA_BASE["Paramount+"] = 0.24

MOTIVOS = {
    "Preço (motivo econômico em geral)": 58,
    "Custo-benefício / preço alto": 40,
    "Situação financeira": 35,
    "Falta de lançamentos": 28,
    "Catálogo restrito ou pouco interessante": 26,
}

GRUPOS = {
    "Serviço": "servico",
    "Região": "regiao",
    "Faixa de renda": "faixa_renda",
    "Forma de pagamento": "forma_pagamento",
    "Tipo de plano": "plano",
    "Assinatura via pacote": "via_pacote",
    "Teve aumento de preço": "aumento_preco_recente",
}
DISTRIBUICOES = {
    "servico": (SERVICOS, [0.28, 0.14, 0.22, 0.14, 0.08, 0.14]),
    "regiao": (
        ["Sudeste", "Nordeste", "Sul", "Centro-Oeste", "Norte"],
        [0.42, 0.27, 0.14, 0.09, 0.08],
    ),
    "faixa_renda": (
        ["até 2 SM", "2 a 5 SM", "5 a 10 SM", "acima de 10 SM"],
        [0.35, 0.35, 0.20, 0.10],
    ),
    "forma_pagamento": (
        ["cartão de crédito", "pix", "boleto", "débito na operadora", "cartão virtual"],
        [0.50, 0.12, 0.06, 0.17, 0.15],
    ),
    "plano": (["com anúncios", "padrão", "premium"], [0.25, 0.50, 0.25]),
    "via_pacote": (["Sim", "Não"], [0.30, 0.70]),
    "aumento_preco_recente": (["Sim", "Não"], [0.35, 0.65]),
}
CATEGORICAS = list(DISTRIBUICOES)
NUMERICAS = ["meses_assinatura", "horas_mes", "dias_sem_acessar"]
NOMES_MODELOS = ["Random Forest", "Regressão Logística"]
PRECO_PLANO = {"com anúncios": 20.0, "padrão": 40.0, "premium": 55.0}

FAIXAS_MESES = [0, 12, 24, 36, 48, 60]
ROTULOS_FAIXAS = ["0 a 12", "13 a 24", "25 a 36", "37 a 48", "49 a 60"]


@dataclass(frozen=True)
class Regra:
    """Um fator de risco ou de proteção.

    A MESMA regra alimenta a simulação (multiplicador) e a aba de recomendações
    (condição + ação), então as duas nunca saem de sincronia.
    """

    nome: str
    condicao: Callable[[pd.DataFrame], pd.Series]
    multiplicador: float
    acao: str


REGRAS = [
    Regra(
        "Mais de 30 dias sem acessar",
        lambda d: d["dias_sem_acessar"] > 30,
        1.45,
        "Enviar lembrete ou recomendação personalizada após ~2 semanas sem acesso.",
    ),
    Regra(
        "Mais de 15 horas assistidas por mês",
        lambda d: d["horas_mes"] > 15,
        0.7,
        "Fator de proteção: estimular o uso (listas, notificação de novos episódios).",
    ),
    Regra(
        "Teve aumento de preço recente",
        lambda d: d["aumento_preco_recente"] == "Sim",
        1.3,
        "Oferecer desconto temporário ou migração para o plano com anúncios.",
    ),
    Regra(
        "Assinatura via pacote",
        lambda d: d["via_pacote"] == "Sim",
        0.7,
        "Fator de proteção: ampliar parcerias e pacotes com operadoras.",
    ),
    Regra(
        "Paga por boleto ou Pix",
        lambda d: d["forma_pagamento"].isin(["boleto", "pix"]),
        1.3,
        "Incentivar cobrança recorrente (cartão virtual) e avisar antes do vencimento.",
    ),
    Regra(
        "Renda até 2 salários mínimos",
        lambda d: d["faixa_renda"] == "até 2 SM",
        1.2,
        "Oferecer plano com anúncios, mais barato, antes do cancelamento.",
    ),
    Regra(
        "Plano premium",
        lambda d: d["plano"] == "premium",
        0.8,
        "Fator de proteção: oferecer upgrade com período de teste.",
    ),
    Regra(
        "Mais de 24 meses de assinatura",
        lambda d: d["meses_assinatura"] > 24,
        0.8,
        "Fator de proteção: concentrar a retenção nos primeiros 24 meses.",
    ),
]
