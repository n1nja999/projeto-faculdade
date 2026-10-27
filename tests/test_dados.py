import pandas as pd
import pytest

from painel.config import CATEGORICAS, DISTRIBUICOES, NUMERICAS, REGRAS
from painel.dados import simular_clientes


@pytest.fixture(scope="module")
def clientes():
    return simular_clientes(n=30_000, semente=11)


def test_colunas_e_tamanho(clientes):
    assert len(clientes) == 30_000
    assert set(CATEGORICAS + NUMERICAS + ["cancelou"]) <= set(clientes.columns)


def test_mesma_semente_gera_os_mesmos_dados():
    pd.testing.assert_frame_equal(simular_clientes(500, 1), simular_clientes(500, 1))


def test_sementes_diferentes_geram_dados_diferentes():
    assert not simular_clientes(500, 1).equals(simular_clientes(500, 2))


def test_alvo_binario_e_taxa_plausivel(clientes):
    assert set(clientes["cancelou"].unique()) <= {0, 1}
    assert 0.15 < clientes["cancelou"].mean() < 0.35


def test_categorias_sorteadas_sao_validas(clientes):
    for coluna, (opcoes, _) in DISTRIBUICOES.items():
        assert set(clientes[coluna]) <= set(opcoes)


def test_probabilidades_de_cada_coluna_somam_um():
    for coluna, (opcoes, probs) in DISTRIBUICOES.items():
        assert len(opcoes) == len(probs), coluna
        assert sum(probs) == pytest.approx(1.0), coluna


def test_regras_devolvem_mascara_booleana(clientes):
    nomes = [r.nome for r in REGRAS]
    assert len(nomes) == len(set(nomes))
    for regra in REGRAS:
        mascara = regra.condicao(clientes)
        assert mascara.dtype == bool
        assert len(mascara) == len(clientes)
        assert regra.multiplicador > 0


@pytest.mark.parametrize("regra", REGRAS, ids=lambda r: r.nome)
def test_fator_de_risco_aumenta_e_de_protecao_reduz_o_cancelamento(clientes, regra):
    mascara = regra.condicao(clientes)
    com = clientes.loc[mascara, "cancelou"].mean()
    sem = clientes.loc[~mascara, "cancelou"].mean()
    if regra.multiplicador > 1:
        assert com > sem
    else:
        assert com < sem
