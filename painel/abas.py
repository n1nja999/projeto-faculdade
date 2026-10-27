from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from .config import (
    FAIXAS_MESES,
    GRUPOS,
    LIMIAR_MAX,
    LIMIAR_MIN,
    LIMIAR_PADRAO,
    LIMIAR_PASSO,
    MOTIVOS,
    PRECO_PLANO,
    REGRAS,
    ROTULOS_FAIXAS,
    SERVICOS,
    TAXA_2022,
    TAXA_2023,
)
from .estilo import (
    COR_APOIO,
    COR_CANCELOU,
    COR_CONTINUOU,
    COR_DESTAQUE,
    COR_MUDO,
    CORES_SERVICO,
    brl,
    insight,
    inteiro_br,
    negrito,
    pct,
    secao,
)
from .graficos import barras, barras_agrupadas, estilizar, mostrar
from .modelos import Resultado, calcular_ganhos, calcular_metricas, tabela_confusao

def aba_visao_geral(filtrados: pd.DataFrame) -> None:
    taxa_servico = filtrados.groupby("servico")["cancelou"].mean() * 100
    lider = taxa_servico.idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de clientes", inteiro_br(len(filtrados)))
    col2.metric("Cancelaram", inteiro_br(int(filtrados["cancelou"].sum())))
    col3.metric("Taxa geral de cancelamento", pct(filtrados["cancelou"].mean() * 100))
    col4.metric("Serviço com mais cancelamento", lider)

    secao("Cancelamento por serviço (%)")
    barras(taxa_servico, cores=CORES_SERVICO, fmt=pct)
    insight(
        f"Com os filtros atuais, {negrito(lider)} lidera com {taxa_servico.max():.1f}% "
        f"de cancelamento. O serviço com menos cancelamento é "
        f"{negrito(taxa_servico.idxmin())} ({taxa_servico.min():.1f}%)."
    )

def aba_por_grupo(filtrados: pd.DataFrame) -> None:
    escolha = st.selectbox("Separar os clientes por:", list(GRUPOS))
    coluna = GRUPOS[escolha]

    resumo = filtrados.groupby(coluna)["cancelou"].agg(["count", "sum", "mean"])
    taxa_grupo = resumo["mean"] * 100

    secao(f"Cancelamento por {escolha.lower()} (%)")
    barras(
        taxa_grupo,
        cores=CORES_SERVICO if coluna == "servico" else None,
        fmt=pct,
        horizontal=True,
    )
    insight(
        f"Maior taxa: {negrito(taxa_grupo.idxmax())} ({taxa_grupo.max():.1f}%). "
        f"Menor taxa: {negrito(taxa_grupo.idxmin())} ({taxa_grupo.min():.1f}%)."
    )

    tabela = resumo[["count", "sum"]].set_axis(["Clientes", "Cancelaram"], axis=1)
    tabela["Taxa (%)"] = taxa_grupo.round(1)
    st.dataframe(tabela)

def aba_comportamento(filtrados: pd.DataFrame) -> None:
    medias = filtrados.groupby("cancelou")[["dias_sem_acessar", "horas_mes"]].mean()
    medias.index = medias.index.map({0: "Continuou", 1: "Cancelou"})
    cores = {"Continuou": COR_CONTINUOU, "Cancelou": COR_CANCELOU}

    col1, col2 = st.columns(2)
    with col1:
        secao("Média de dias sem acessar")
        barras(medias["dias_sem_acessar"], cores=cores, ordenar=False, altura=280)
    with col2:
        secao("Média de horas assistidas por mês")
        barras(medias["horas_mes"], cores=cores, ordenar=False, altura=280)

    faixas = pd.cut(filtrados["meses_assinatura"], FAIXAS_MESES, labels=ROTULOS_FAIXAS)
    por_faixa = filtrados.groupby(faixas, observed=True)["cancelou"].agg(["mean", "count"])
    taxa_faixa = por_faixa["mean"] * 100
    media_geral = filtrados["cancelou"].mean() * 100

    secao("Cancelamento por tempo de assinatura, em meses (%)")
    st.caption(
        f"A linha tracejada é a média geral ({media_geral:.1f}%). "
        "Barras em âmbar estão acima da média."
    )
    barras(
        taxa_faixa,
        fmt=pct,
        ordenar=False,
        altura=300,
        referencia=media_geral,
        contagem=por_faixa["count"],
    )
    if len(taxa_faixa) >= 2:
        texto = (
            f"Na primeira faixa ({taxa_faixa.index[0]} meses) o cancelamento é "
            f"{negrito(pct(taxa_faixa.iloc[0]))}; na última, {negrito(pct(taxa_faixa.iloc[-1]))}."
        )
        quedas = taxa_faixa.diff().iloc[1:]
        if quedas.min() < 0:
            pos = taxa_faixa.index.get_loc(quedas.idxmin())
            texto += (
                f" A maior queda acontece entre {negrito(taxa_faixa.index[pos - 1])} "
                f"e {negrito(taxa_faixa.index[pos])} meses."
            )
        insight(texto)
        st.caption(
            "Nos dados simulados, esse efeito vem da regra que reduz o risco "
            "depois de 24 meses de assinatura."
        )


@st.fragment
def aba_modelo_previsao(
    dados: pd.DataFrame, resultado: Resultado, servicos_escolhidos: list[str]
) -> None:
    y_teste = resultado.y_teste
    probabilidades = resultado.proba["Random Forest"]

    st.write("O modelo Random Forest aprende com os dados e tenta prever quem vai cancelar.")
    limite = st.slider(
        "A partir de qual risco o modelo diz que o cliente vai cancelar?",
        LIMIAR_MIN, LIMIAR_MAX, LIMIAR_PADRAO, LIMIAR_PASSO,
    )
    metricas = calcular_metricas(y_teste, probabilidades, limite)
    previsao = (probabilidades >= limite).astype(int)

    col1, col2, col3 = st.columns(3)
    col1.metric("Acurácia", round(metricas["Acurácia"], 3))
    col2.metric("Precisão", round(metricas["Precisão"], 3))
    col3.metric("Recall", round(metricas["Recall"], 3))

    secao("Acertos e erros do modelo")
    st.dataframe(tabela_confusao(y_teste, previsao))

    secao("O que mais pesa na decisão do modelo")
    st.caption("Importância por permutação: quanto o ROC-AUC cai quando a variável é embaralhada.")
    barras(resultado.importancia.head(10), fmt=lambda v: f"{v:.3f}", horizontal=True)

    secao("Clientes com maior risco de cancelar")
    teste = dados.loc[resultado.indices_teste].assign(risco_de_cancelar=probabilidades)
    teste = teste[teste["servico"].isin(servicos_escolhidos)]
    st.dataframe(
        teste.nlargest(20, "risco_de_cancelar"),
        column_config={
            "risco_de_cancelar": st.column_config.ProgressColumn(
                "Risco de cancelar", min_value=0.0, max_value=1.0, format="%.2f"
            )
        },
    )

def aba_pesquisa(dados: pd.DataFrame) -> None:
    st.write(
        "Pesquisa da Hibou com 1.400 pessoas: porcentagem de entrevistados que já cancelou cada serviço."
    )
    pesquisa = pd.DataFrame({"2022 (%)": TAXA_2022, "2023 (%)": TAXA_2023})
    pesquisa["Variação (pontos)"] = pesquisa["2023 (%)"] - pesquisa["2022 (%)"]

    secao("Taxa de cancelamento em 2023 (%)")
    barras(pesquisa["2023 (%)"], cores=CORES_SERVICO, fmt=lambda v: f"{v:.0f}%")
    st.dataframe(pesquisa)

    secao("Principais motivos para cancelar (% dos entrevistados)")
    barras(pd.Series(MOTIVOS), fmt=lambda v: f"{v:.0f}%", horizontal=True)

    secao("Pesquisa x simulação")
    comparacao = pd.DataFrame(index=SERVICOS)
    comparacao["Pesquisa 2023 (%)"] = pd.Series(TAXA_2023)
    comparacao["Simulação (%)"] = (dados.groupby("servico")["cancelou"].mean() * 100).round(1)
    barras_agrupadas(comparacao)
    st.dataframe(comparacao)

    st.caption("O Paramount+ não aparece na pesquisa. Usei 24%, a média dos outros cinco serviços.")
    st.markdown(
        "Fonte: Hibou (2023), divulgada pelo site "
        "[Minha Operadora](https://www.minhaoperadora.com.br/2023/04/maior-taxa-de-cancelamentos-de-streaming-e-da-netflix-veja-o-ranking.html)."
    )

@st.fragment
def aba_comparacao(resultado: Resultado, modelo_escolhido: str) -> None:
    st.write(
        "Comparação entre a **Regressão Logística** (simples e interpretável, serve de "
        "linha de base) e o **Random Forest** (mais flexível)."
    )
    st.warning(
        "Demonstração com dados sintéticos: os modelos redescobrem as regras usadas para "
        "gerar os dados, então as métricas não representam clientes reais."
    )
    limite = st.slider(
        "Limiar de risco para considerar que o cliente vai cancelar",
        LIMIAR_MIN, LIMIAR_MAX, LIMIAR_PADRAO, LIMIAR_PASSO,
        key="limite_comparacao",
    )

    y_teste = resultado.y_teste
    comparacao_modelos = pd.DataFrame(
        {nome: calcular_metricas(y_teste, proba, limite) for nome, proba in resultado.proba.items()}
    ).T.round(3)
    comparacao_modelos["ROC-AUC validação cruzada"] = [
        f"{resultado.cv[nome][0]:.3f} ± {resultado.cv[nome][1]:.3f}"
        for nome in comparacao_modelos.index
    ]
    secao("Métricas no limiar escolhido")
    st.dataframe(comparacao_modelos)
    st.caption(
        "Com ~25% de cancelamentos a acurácia engana (um modelo que sempre diz "
        '"continua" já acerta ~75%). Olhe F1, ROC-AUC e PR-AUC. Se o Random Forest '
        "não ganhar de forma clara, o modelo mais simples é preferível."
    )

    secao(f"Acertos e erros ({modelo_escolhido})")
    previsao = (resultado.proba[modelo_escolhido] >= limite).astype(int)
    st.dataframe(tabela_confusao(y_teste, previsao))

    col1, col2 = st.columns(2)
    with col1:
        secao("O que mais pesa no Random Forest")
        st.caption("Importância por permutação.")
        barras(resultado.importancia, fmt=lambda v: f"{v:.3f}", horizontal=True)
    with col2:
        secao("Maiores coeficientes da Regressão Logística")
        st.caption("Vermelho aumenta o risco de cancelar; verde diminui.")
        coef = resultado.coeficientes
        top = coef.reindex(coef.abs().sort_values(ascending=False).head(10).index)
        barras(top, fmt=lambda v: f"{v:+.2f}", horizontal=True, divergente=True)

@st.fragment
def aba_custo_do_erro(resultado: Resultado, modelo_escolhido: str) -> None:
    st.write(
        "O limiar do modelo é uma decisão de negócio. Limiar baixo: a empresa oferece "
        "retenção para muita gente (gasta mais). Limiar alto: deixa de abordar clientes "
        "que iriam cancelar (perde receita). Ajuste os valores hipotéticos:"
    )
    col1, col2, col3 = st.columns(3)
    valor_cliente = col1.number_input(
        "Valor de um cliente retido (R$)", min_value=0, value=480, step=20,
        help="Exemplo: R$ 40 por mês x 12 meses.",
    )
    custo_oferta = col2.number_input(
        "Custo da oferta de retenção por cliente (R$)", min_value=0, value=30, step=5
    )
    taxa_sucesso = col3.slider("Chance de a oferta evitar o cancelamento", 0.05, 1.0, 0.30, 0.05)

    y_real = resultado.y_teste.to_numpy()
    ganhos = calcular_ganhos(
        y_real, resultado.proba[modelo_escolhido], valor_cliente, custo_oferta, taxa_sucesso
    )

    st.write("")
    col1, col2, col3 = st.columns(3)
    col1.metric("Melhor limiar", f"{ganhos.idxmax():.2f}")
    col2.metric("Ganho líquido nesse limiar", brl(ganhos.max()))
    col3.metric("Ganho se abordar todos (limiar 0)", brl(ganhos.loc[0.0]))

    secao("Ganho líquido por limiar (conjunto de teste)")
    df = ganhos.rename("ganho").rename_axis("limiar").reset_index()
    melhor = df[df["limiar"] == ganhos.idxmax()]
    dica = [
        alt.Tooltip("limiar:Q", title="Limiar", format=".2f"),
        alt.Tooltip("ganho:Q", title="Ganho (R$)", format=",.0f"),
    ]
    area = (
        alt.Chart(df)
        .mark_area(opacity=0.18, color=COR_APOIO, line={"color": COR_APOIO, "strokeWidth": 3})
        .encode(
            x=alt.X("limiar:Q", title="Limiar de risco", axis=alt.Axis(grid=False)),
            y=alt.Y("ganho:Q", title="Ganho líquido (R$)"),
            tooltip=dica,
        )
    )
    zero = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(color=COR_MUDO, strokeDash=[4, 4])
        .encode(y="y:Q")
    )
    ponto = (
        alt.Chart(melhor)
        .mark_point(filled=True, size=180, color=COR_DESTAQUE, opacity=1)
        .encode(x="limiar:Q", y="ganho:Q", tooltip=dica)
    )
    mostrar(estilizar((area + zero + ponto).properties(height=340)))
    insight(f"O ponto âmbar marca o limiar de maior ganho: {negrito(f'{ganhos.idxmax():.2f}')}.")
    st.caption(
        "Ganho = clientes que iam cancelar e foram retidos x valor do cliente "
        "- todos os clientes abordados x custo da oferta. Valores hipotéticos, "
        f"calculados sobre os {len(y_real)} clientes do conjunto de teste ({modelo_escolhido})."
    )


def aba_recomendacoes(filtrados: pd.DataFrame) -> None:
    st.write(
        "Compara a taxa de cancelamento de quem tem o fator com a de quem não tem, "
        "com uma ação de retenção para cada um."
    )
    linhas = []
    for regra in REGRAS:
        por_mascara = filtrados["cancelou"].groupby(regra.condicao(filtrados)).agg(["mean", "count"])
        if len(por_mascara) < 2:
            continue
        com_fator = por_mascara.loc[True, "mean"] * 100
        sem_fator = por_mascara.loc[False, "mean"] * 100
        linhas.append(
            {
                "Fator": regra.nome,
                "Clientes com o fator": int(por_mascara.loc[True, "count"]),
                "Cancelamento com o fator (%)": round(com_fator, 1),
                "Cancelamento sem o fator (%)": round(sem_fator, 1),
                "Diferença (p.p.)": round(com_fator - sem_fator, 1),
                "Ação sugerida": regra.acao,
            }
        )

    if linhas:
        tabela = pd.DataFrame(linhas).sort_values("Diferença (p.p.)", ascending=False)
        secao("Diferença na taxa de cancelamento (pontos percentuais)")
        st.caption("Vermelho: o fator aumenta o cancelamento. Verde: protege contra o cancelamento.")
        barras(
            tabela.set_index("Fator")["Diferença (p.p.)"],
            fmt=lambda v: f"{v:+.1f}",
            horizontal=True,
            divergente=True,
        )
        st.dataframe(tabela, hide_index=True)
        st.caption(
            "Os efeitos vêm das regras usadas para simular os dados. Com dados reais, "
            "esta tabela mostraria os efeitos observados de fato."
        )
    else:
        st.info(
            "Com os serviços escolhidos não dá para comparar nenhum fator "
            "(todos os clientes têm ou não têm o fator). Selecione mais serviços."
        )

    secao("Receita mensal perdida com os cancelamentos")
    st.caption("Preços hipotéticos por plano.")
    cancelados = filtrados[filtrados["cancelou"] == 1]
    receita_perdida = cancelados["plano"].map(PRECO_PLANO)
    receita_total = filtrados["plano"].map(PRECO_PLANO).sum()

    col1, col2 = st.columns(2)
    col1.metric("Receita mensal perdida", brl(receita_perdida.sum()))
    col2.metric("% da receita mensal", pct(receita_perdida.sum() / receita_total * 100))

    secao("Receita mensal perdida por serviço (R$)")
    barras(receita_perdida.groupby(cancelados["servico"]).sum(), cores=CORES_SERVICO, fmt=brl)
    st.caption(
        "Preços assumidos: "
        + ", ".join(f"{plano} = R$ {valor:.0f}" for plano, valor in PRECO_PLANO.items())
        + "."
    )

def aba_limitacoes():
    st.markdown("""
**Limitações do trabalho**

- **Dados sintéticos:** os clientes foram simulados com regras escritas por nós. Os modelos
  redescobrem essas regras, então as métricas e a importância das variáveis não provam nada
  sobre clientes reais.
- **Taxa acumulada vs. probabilidade:** a Hibou mede quem *já cancelou* o serviço alguma vez
  (acumulado ao longo do tempo). Aqui esse número foi usado como chance de cancelamento
  de cada cliente em um único momento, uma simplificação.
- **Paramount+ estimado:** o serviço não aparece na pesquisa e usa 24% como estimativa.
- **Margem de erro:** com 1.400 entrevistados, cada taxa da pesquisa tem margem de erro
  de poucos pontos percentuais.
- **Variáveis independentes:** as colunas são sorteadas separadamente, então relações reais
  (ex.: horas assistidas x dias sem acessar, renda x plano) não existem nos dados.
- **Preços e custos hipotéticos:** os valores das abas "Custo do erro" e "Recomendações"
  são exemplos para ilustrar o raciocínio.
- **Dados de 2023:** o cenário do streaming muda rápido e a pesquisa pode estar desatualizada.
- **Escala:** 10.000 clientes cabem em memória no pandas, então o volume não caracteriza
  Big Data.
        """)
