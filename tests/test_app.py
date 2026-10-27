from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def rodar(monkeypatch, modo):
    monkeypatch.setenv("PAINEL_NAVEGACAO", modo)
    return AppTest.from_file(APP, default_timeout=300).run()


def test_modo_abas_renderiza_as_9_abas(monkeypatch):
    at = rodar(monkeypatch, "abas")
    assert not at.exception
    assert len(at.tabs) == 9


def test_modo_lazy_renderiza_so_a_secao_escolhida(monkeypatch):
    at = rodar(monkeypatch, "lazy")
    assert not at.exception
    assert len(at.tabs) == 0
    assert "Total de clientes" in [m.label for m in at.metric]

    at.radio(key="secao_ativa").set_value("Custo do erro").run()
    assert not at.exception
    rotulos = [m.label for m in at.metric]
    assert "Melhor limiar" in rotulos
    assert "Total de clientes" not in rotulos


def test_filtro_sem_servico_mostra_aviso(monkeypatch):
    at = rodar(monkeypatch, "abas")
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert any("pelo menos um serviço" in w.value for w in at.warning)
