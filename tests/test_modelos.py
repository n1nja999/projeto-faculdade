import numpy as np
import pytest

from painel.dados import simular_clientes
from painel.modelos import calcular_ganhos, calcular_metricas, tabela_confusao, treinar


def test_ganhos_com_exemplo_calculado_a_mao():
    y = np.array([1, 1, 0, 0])
    proba = np.array([0.9, 0.6, 0.4, 0.1])
    g = calcular_ganhos(y, proba, valor_cliente=100, custo_oferta=10, taxa_sucesso=0.5)

    assert g.loc[0.0] == pytest.approx(60)  # aborda 4, retém 2: 2*0.5*100 - 4*10
    assert g.loc[0.5] == pytest.approx(80)  # aborda 2, retém 2: 100 - 20
    assert g.loc[0.95] == 0  # ninguém é abordado
    assert g.idxmax() == 0.45  # primeiro limiar com o ganho máximo (80)


def test_metricas_de_modelo_perfeito():
    y = np.array([0, 0, 1, 1])
    proba = np.array([0.1, 0.2, 0.8, 0.9])
    m = calcular_metricas(y, proba, limite=0.5)
    for nome in ["Acurácia", "Precisão", "Recall", "F1", "ROC-AUC", "PR-AUC"]:
        assert m[nome] == pytest.approx(1.0), nome


def test_metricas_nao_quebram_quando_ninguem_e_previsto_como_cancelamento():
    y = np.array([0, 0, 1, 1])
    proba = np.array([0.1, 0.2, 0.8, 0.9])
    m = calcular_metricas(y, proba, limite=0.95)
    assert m["Precisão"] == 0 and m["Recall"] == 0


def test_tabela_confusao():
    t = tabela_confusao(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 1]))
    assert t.to_numpy().tolist() == [[1, 1], [0, 2]]


@pytest.fixture(scope="module")
def resultado():
    return treinar(simular_clientes(n=1500, semente=5))


def test_treinar_devolve_probabilidades_validas(resultado):
    assert len(resultado.y_teste) == 375  # 25% de 1500
    for proba in resultado.proba.values():
        assert proba.shape == (375,)
        assert proba.min() >= 0 and proba.max() <= 1


def test_modelos_aprendem_algo_alem_do_acaso(resultado):
    for media, _ in resultado.cv.values():
        assert media > 0.55


def test_importancia_vem_ordenada_e_coeficientes_tem_variaveis_numericas(resultado):
    assert resultado.importancia.is_monotonic_decreasing
    assert "dias_sem_acessar" in resultado.coeficientes.index
