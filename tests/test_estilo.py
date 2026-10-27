from painel.estilo import brl, inteiro_br, negrito, pct


def test_negrito_escapa_html():
    assert negrito("<img src=x onerror=alert(1)>") == "<b>&lt;img src=x onerror=alert(1)&gt;</b>"


def test_formatadores():
    assert pct(25.14) == "25.1%"
    assert inteiro_br(10000) == "10.000"
    assert brl(1234) == "R$ 1.234"
    assert brl(-1234) == "-R$ 1.234"
