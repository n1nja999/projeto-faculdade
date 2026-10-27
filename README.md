# Taxa de cancelamento de streaming no Brasil

Painel em Streamlit: clientes simulados (calibrados pela pesquisa Hibou 2023),
dois modelos de previsão (Regressão Logística e Random Forest) e análise de custo.

## Requisitos pra rodar:

    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run taxa_de_cancelamento.py

Modo mais rápido (renderiza só a seção escolhida, em vez das 9 abas):

    PAINEL_NAVEGACAO=lazy streamlit run taxa_de_cancelamento.py          # Windows (PowerShell): $env:PAINEL_NAVEGACAO="lazy"; streamlit run taxa_de_cancelamento.py

## Testes

    pip install -r requirements-dev.txt
    pytest

## Estrutura

    taxa_de_cancelamento.py  ponto de entrada
    painel/config.py     constantes, distribuições e REGRAS (fonte única da simulação e das recomendações)
    painel/dados.py      simulação dos clientes
    painel/modelos.py    treino, métricas e ganho por limiar
    painel/estilo.py     cores, CSS e helpers de HTML seguro
    painel/graficos.py   gráficos Altair
    painel/abas.py       conteúdo de cada aba
    painel/principal.py  montagem da página e navegação
    tests/               testes com pytest
