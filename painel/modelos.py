from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CATEGORICAS, NUMERICAS, SEMENTE


@dataclass(frozen=True)
class Resultado:
    indices_teste: pd.Index
    y_teste: pd.Series
    proba: dict[str, np.ndarray]
    cv: dict[str, tuple[float, float]]
    importancia: pd.Series
    coeficientes: pd.Series


def montar_pipeline(modelo, escalar_numericas: bool) -> Pipeline:
    numericas = StandardScaler() if escalar_numericas else "passthrough"
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
            ("num", numericas, NUMERICAS),
        ]
    )
    return Pipeline([("pre", pre), ("modelo", modelo)])


def treinar(dados: pd.DataFrame) -> Resultado:
    """Treina os dois modelos. Função pura: dá pra testar sem Streamlit."""
    X = dados[CATEGORICAS + NUMERICAS]
    y = dados["cancelou"]
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=SEMENTE, stratify=y
    )

    rf = montar_pipeline(
        RandomForestClassifier(n_estimators=150, max_depth=8, random_state=SEMENTE, n_jobs=-1),
        escalar_numericas=False,
    )
    lr = montar_pipeline(LogisticRegression(max_iter=1000), escalar_numericas=True)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
    cv_rf = cross_val_score(rf, X, y, cv=cv, scoring="roc_auc")  # RF já paraleliza por dentro
    cv_lr = cross_val_score(lr, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)

    rf.fit(X_treino, y_treino)
    lr.fit(X_treino, y_treino)

    perm = permutation_importance(
        rf, X_teste, y_teste, scoring="roc_auc", n_repeats=5, random_state=SEMENTE, n_jobs=-1
    )
    importancia = pd.Series(perm.importances_mean, index=X.columns).sort_values(ascending=False)

    nomes = pd.Index(lr.named_steps["pre"].get_feature_names_out())
    nomes = nomes.str.replace(r"^(cat|num)__", "", regex=True)
    coeficientes = pd.Series(lr.named_steps["modelo"].coef_[0], index=nomes)

    return Resultado(
        indices_teste=X_teste.index,
        y_teste=y_teste,
        proba={
            "Random Forest": rf.predict_proba(X_teste)[:, 1],
            "Regressão Logística": lr.predict_proba(X_teste)[:, 1],
        },
        cv={
            "Random Forest": (cv_rf.mean(), cv_rf.std()),
            "Regressão Logística": (cv_lr.mean(), cv_lr.std()),
        },
        importancia=importancia,
        coeficientes=coeficientes,
    )

@st.cache_resource(show_spinner="Treinando os modelos (só na primeira vez)...")
def treinar_modelos(dados: pd.DataFrame) -> Resultado:
    return treinar(dados)


def calcular_metricas(y_real, proba: np.ndarray, limite: float) -> dict[str, float]:
    previsao = (proba >= limite).astype(int)
    return {
        "Acurácia": accuracy_score(y_real, previsao),
        "Precisão": precision_score(y_real, previsao, zero_division=0),
        "Recall": recall_score(y_real, previsao, zero_division=0),
        "F1": f1_score(y_real, previsao, zero_division=0),
        "ROC-AUC": roc_auc_score(y_real, proba),
        "PR-AUC": average_precision_score(y_real, proba),
    }


def tabela_confusao(y_real, previsao) -> pd.DataFrame:
    return pd.DataFrame(
        confusion_matrix(y_real, previsao),
        index=["Realmente continuou", "Realmente cancelou"],
        columns=["Modelo previu: continua", "Modelo previu: cancela"],
    )

def calcular_ganhos(
    y_real: np.ndarray,
    proba: np.ndarray,
    valor_cliente: float,
    custo_oferta: float,
    taxa_sucesso: float,
) -> pd.Series:
    limiares = np.round(np.arange(0.0, 0.951, 0.05), 2)
    marcados = proba[None, :] >= limiares[:, None] 
    abordados = marcados.sum(axis=1)
    verdadeiros_positivos = (marcados & (y_real == 1)).sum(axis=1)
    ganho = verdadeiros_positivos * taxa_sucesso * valor_cliente - abordados * custo_oferta
    return pd.Series(ganho, index=limiares, name="Ganho líquido (R$)")
