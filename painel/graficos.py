from __future__ import annotations

import inspect
from typing import Callable

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from .estilo import (
    COR_APOIO,
    COR_CANCELOU,
    COR_CONTINUOU,
    COR_DESTAQUE,
    COR_LINHA,
    COR_MUDO,
    COR_NEUTRA,
    COR_TEXTO,
    numero,
)

_ALTAIR_USA_WIDTH = "width" in inspect.signature(st.altair_chart).parameters


def mostrar(grafico: alt.TopLevelMixin) -> None:
    if _ALTAIR_USA_WIDTH:
        st.altair_chart(grafico, width="stretch")
    else:
        st.altair_chart(grafico, use_container_width=True)


def estilizar(grafico: alt.TopLevelMixin) -> alt.TopLevelMixin:
    return (
        grafico.configure(background="transparent")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=COR_MUDO,
            labelFontSize=12,
            gridColor=COR_LINHA,
            domainColor=COR_LINHA,
            tickColor=COR_LINHA,
        )
        .configure_legend(labelColor=COR_TEXTO, labelFontSize=12)
    )

def _dados_barras(
    serie: pd.Series,
    fmt: Callable[[float], str],
    cores: dict[str, str] | None,
    divergente: bool,
    referencia: float | None,
    contagem: pd.Series | None,
) -> pd.DataFrame:
    df = serie.rename("valor").reset_index()
    df.columns = ["categoria", "valor"]
    df["categoria"] = df["categoria"].astype(str)
    df["rotulo"] = df["valor"].map(fmt)
    if contagem is not None:
        df["clientes"] = np.asarray(contagem)

    if divergente:
        df["cor"] = np.where(df["valor"] >= 0, COR_CANCELOU, COR_CONTINUOU)
    elif cores:
        df["cor"] = df["categoria"].map(cores).fillna(COR_NEUTRA)
    elif referencia is not None:
        df["cor"] = np.where(df["valor"] > referencia, COR_DESTAQUE, COR_NEUTRA)
    else:
        df["cor"] = np.where(df["valor"] == df["valor"].max(), COR_DESTAQUE, COR_NEUTRA)
    return df

def barras(
    serie: pd.Series,
    *,
    cores: dict[str, str] | None = None,
    fmt: Callable[[float], str] = numero,
    horizontal: bool = False,
    ordenar: bool = True,
    divergente: bool = False,
    altura: int = 320,
    referencia: float | None = None,
    contagem: pd.Series | None = None,
) -> None:
    """Gráfico de barras com rótulos.

    Cor: `divergente` (vermelho/verde pelo sinal) > `cores` (por categoria) >
    `referencia` (âmbar acima da linha tracejada) > âmbar na maior barra.
    """
    df = _dados_barras(serie, fmt, cores, divergente, referencia, contagem)
    ordem = (
        df.sort_values("valor", ascending=False)["categoria"].tolist()
        if ordenar
        else df["categoria"].tolist()
    )
    base = alt.Chart(df)
    dica = [alt.Tooltip("categoria:N", title="Item"), alt.Tooltip("rotulo:N", title="Valor")]
    if contagem is not None:
        dica.append(alt.Tooltip("clientes:Q", title="Clientes", format=",.0f"))
    cor = alt.Color("cor:N", scale=None, legend=None)

    if horizontal:
        enc = dict(
            y=alt.Y("categoria:N", sort=ordem, title=None,
                    axis=alt.Axis(labelLimit=280, grid=False)),
            x=alt.X("valor:Q", title=None, axis=alt.Axis(grid=True)),
        )
        barra = base.mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, size=22)
        texto = base.mark_text(align="left", dx=6, color=COR_TEXTO, fontSize=12, fontWeight=600)
        altura = 36 * len(df) + 24
    else:
        enc = dict(
            x=alt.X("categoria:N", sort=ordem, title=None,
                    axis=alt.Axis(labelAngle=0, grid=False, labelLimit=140)),
            y=alt.Y("valor:Q", title=None),
        )
        barra = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        texto = base.mark_text(baseline="bottom", dy=-5, color=COR_TEXTO, fontSize=12, fontWeight=600)

    camadas = barra.encode(**enc, color=cor, tooltip=dica)
    if not divergente:
        camadas = camadas + texto.encode(**enc, text="rotulo:N")
    if referencia is not None:
        eixo_ref = dict(x="ref:Q") if horizontal else dict(y=alt.Y("ref:Q", title=None))
        linha = (
            alt.Chart(pd.DataFrame({"ref": [referencia]}))
            .mark_rule(color=COR_TEXTO, strokeDash=[5, 4], opacity=0.7)
            .encode(**eixo_ref)
        )
        camadas = camadas + linha
    mostrar(estilizar(camadas.properties(height=altura)))

def barras_agrupadas(df: pd.DataFrame, altura: int = 340) -> None:
    longo = (
        df.rename_axis("servico")
        .reset_index()
        .melt(id_vars="servico", var_name="fonte", value_name="valor")
        .dropna()
    )
    grafico = (
        alt.Chart(longo)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("servico:N", title=None, axis=alt.Axis(labelAngle=0, grid=False)),
            xOffset="fonte:N",
            y=alt.Y("valor:Q", title=None),
            color=alt.Color(
                "fonte:N",
                scale=alt.Scale(range=[COR_DESTAQUE, COR_APOIO]),
                legend=alt.Legend(orient="top", title=None),
            ),
            tooltip=[
                alt.Tooltip("servico:N", title="Serviço"),
                alt.Tooltip("fonte:N", title="Fonte"),
                alt.Tooltip("valor:Q", title="Taxa (%)", format=".1f"),
            ],
        )
        .properties(height=altura)
    )
    mostrar(estilizar(grafico))
