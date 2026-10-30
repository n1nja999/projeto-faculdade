# 📊 Taxa de Cancelamento de Streaming no Brasil

### Análise Preditiva de Cancelamento, Comportamento do Usuário e Otimização Financeira

Painel interativo desenvolvido em **Streamlit** com **10.000 clientes simulados** (calibrados com base na pesquisa de mercado Hibou 2023), modelagem preditiva supervisionada (**Regressão Logística** e **Random Forest**), análise de custo do erro e recomendações prescritivas de retenção.

## 🎯 Visão Geral e Objetivos

O mercado de **Subscription Video on Demand (SVOD)** no Brasil opera sob forte concorrência e custos crescentes de aquisição. Este projeto resolve a seguinte questão de negócio:

> **Pergunta de pesquisa:** _Quais fatores mais aumentam o risco de cancelamento de uma assinatura de streaming e é possível prever quem vai cancelar com antecedência analítica?_

Para responder a essa pergunta, o projeto articula:

1. **Calibração Realista:** Distribuição amostral ancorada na pesquisa nacional de campo da **Hibou (1.400 respondentes)**.
2. **Engenharia de Regras e Simulação:** Módulo unificado de dados que reflete elasticidade de preço, modalidade de contratação (avulsa vs. pacote/combo) e engajamento de tela.
3. **Previsão de Evasão:** Modelos de Machine Learning avaliados sob curva ROC-AUC, permutação de atributos e ganho financeiro por limiar de decisão (_threshold_).
4. **Painel Dinâmico:** Interface web com 9 abas analíticas e suporte a renderização otimizada sob demanda.


## 📈 Panorama Geral da Base (10.000 Clientes)

| Métrica                                      | Valor Consolidado               |
| :------------------------------------------- | :------------------------------ |
| **Total de Clientes na Base**                | `10.000`                        |
| **Total de Cancelamentos**                   | `2.512`                         |
| **Taxa Média Geral de Cancelamento**         | `25,1%`                         |
| **Serviço com Maior Volume de Cancelamento** | **Netflix (32,0%)**             |
| **Serviço com Menor Volume de Cancelamento** | **HBO Max (13,3%)**             |
| **Perda Mensal Consolidada**                 | **R$ 95.025,00 (24,5% do MRR)** |

### Distribuição e Cancelamento por Serviço

```text
Netflix      ████████████████ 32,0% (913 cancelamentos / 2.849 clientes)
Prime Video  ██████████████   28,6% (632 cancelamentos / 2.213 clientes)
Globoplay    █████████████    27,3% (373 cancelamentos / 1.366 clientes)
Paramount+   ███████████      22,9% (181 cancelamentos /   792 clientes)
Disney+      ████████         16,4% (229 cancelamentos / 1.398 clientes)
HBO Max      ██████           13,3% (184 cancelamentos / 1.382 clientes)
```

## 🔎 Evidências de Mercado (Pesquisa Hibou)

### Motivos Declarados para Cancelamento

A pesquisa com consumidores comprova a primazia das variáveis de custo frente às variáveis de catálogo:

- **Preço (motivo econômico geral):** `58%`
- **Custo-benefício desfavorável / preço alto:** `40%`
- **Dificuldade na situação financeira:** `35%`
- **Falta de lançamentos no catálogo:** `28%`
- **Catálogo restrito ou pouco interessante:** `26%`

### Indicadores Operacionais de Consumo

- **Dias sem login:** clientes retidos têm média de **28,8 dias** sem acesso; evadidos chegam a **32,3 dias**.
- **Consumo mensal:** clientes retidos assistem em média **16,6 horas/mês**, contra **14,3 horas/mês** no grupo que cancelou.
- **Ciclo de vida (Tenure):** o cancelamento é crítico nos primeiros 12 meses (**28,8%**) e cai para **22,4%** a partir do 4º ano de fidelidade.

## 🤖 Modelagem Preditiva

O pipeline compara **Regressão Logística** e **Random Forest**. Para ações de retenção preventiva, o limiar de probabilidade ótimo de corte foi calibrado em **`0,30`**.

### Desempenho do Random Forest (Corte = 0,30)

| Métrica                    | Resultado |
| :------------------------- | :-------- |
| **Acurácia**               | `69,9%`   |
| **Precisão**               | `40,2%`   |
| **Recall (Sensibilidade)** | `40,8%`   |

#### Matriz de Confusão

| Realidade \ Previsão    | Previsto: Continua | Previsto: Cancela | Total Real |
| :---------------------- | :----------------: | :---------------: | :--------: |
| **Realmente continuou** |    `1.491` (VN)    |    `381` (FP)     |   1.872    |
| **Realmente cancelou**  |     `372` (FN)     |    `256` (VP)     |    628     |

### O que mais pesa na decisão do modelo?

_(Importância por permutação calculada pelo decaimento na métrica ROC-AUC)_

```text
servico               ████████████████████ 0,046
via_pacote            ████████████ 0,027
horas_mes             ███████████ 0,025
dias_sem_acessar      █████████ 0,021
aumento_preco_recente ██████ 0,013
faixa_renda           ███ 0,007
plano                 ███ 0,006
meses_assinatura      ██ 0,005
forma_pagamento       █ 0,003
regiao                ▏ 0,001
```

---

## 💸 Impacto Financeiro e Custo do Erro

Assumindo a precificação de mercado (_R$ 20 para plano com anúncios, R$ 40 para padrão e R$ 55 para premium_), o cancelamento gera uma perda mensal de **R$ 95.025,00** (**24,5%** da receita da base):

- 🔴 **Netflix:** R$ 34.120,00 / mês
- 🔵 **Prime Video:** R$ 24.365,00 / mês
- 🟠 **Globoplay:** R$ 14.145,00 / mês
- 🔷 **Disney+:** R$ 8.740,00 / mês
- 🟣 **HBO Max:** R$ 6.880,00 / mês
- 🟢 **Paramount+:** R$ 6.775,00 / mês

---

## 🛡️ Matriz Estratégica de Retenção

Comparação da taxa de cancelamento de clientes com vs. sem cada fator, orientando as regras em `painel/config.py`:

| Fator Avaliado                      | Cancelamento COM o Fator | Cancelamento SEM o Fator |   Impacto   |   Classificação   | Ação Recomendada                                                      |
| :---------------------------------- | :----------------------: | :----------------------: | :---------: | :---------------: | :-------------------------------------------------------------------- |
| **Mais de 30 dias sem acessar**     |          29,5%           |          21,0%           | `+8,5 p.p.` | ⚠️ Fator de Risco | Lembrete ativo, push notification e recomendação personalizada.       |
| **Teve aumento de preço recente**   |          30,3%           |          22,4%           | `+7,9 p.p.` | ⚠️ Fator de Risco | Desconto temporário de retenção ou downgrade para plano com anúncios. |
| **Renda até 2 salários mínimos**    |          29,3%           |          22,9%           | `+6,4 p.p.` | ⚠️ Fator de Risco | Oferta de planos pré-pagos e combos populares subvencionados.         |
| **Paga por boleto ou Pix**          |          30,2%           |          24,0%           | `+6,2 p.p.` | ⚠️ Fator de Risco | Incentivo financeiro para migração para cartão ou débito automático.  |
| **Plano Premium**                   |          20,7%           |          26,6%           | `-5,8 p.p.` | 🛡️ Fator Protetor | Estimular upgrades familiares e benefícios multi-telas.               |
| **Mais de 24 meses de assinatura**  |          22,8%           |          28,6%           | `-5,8 p.p.` | 🛡️ Fator Protetor | Concentrar esforços nos primeiros meses de onboarding.                |
| **Assinatura via pacote (bundle)**  |          19,1%           |          27,7%           | `-8,7 p.p.` | 🛡️ Fator Protetor | Ampliar parcerias com operadoras de telecomunicações e bancos.        |
| **Mais de 15 horas assistidas/mês** |          19,9%           |          29,2%           | `-9,4 p.p.` | 🛡️ Fator Protetor | Estímulo a hábitos de maratona e listas de interesse ativas.          |

---

## 📂 Estrutura do Repositório

```text
├── taxa_de_cancelamento.py   # Ponto de entrada do painel Streamlit
├── painel/
│   ├── config.py             # Constantes, distribuições e REGRAS (fonte única de simulação e recomendações)
│   ├── dados.py              # Gerador e calibrador da base simulada de 10.000 clientes
│   ├── modelos.py            # Treinamento, métricas de avaliação e otimização por limiar
│   ├── estilo.py             # Definição de cores, paleta, CSS e helpers de HTML seguro
│   ├── graficos.py           # Construção e customização visual com Altair
│   ├── abas.py               # Renderização do conteúdo de cada uma das 9 abas
│   └── principal.py          # Montagem da página, layout e orquestração de navegação
├── tests/                    # Testes automatizados com Pytest
├── relatorio_cancelamento_streaming_abnt.html # Relatório formal ABNT NBR 10719 para exportação em PDF
├── requirements.txt          # Dependências do painel e bibliotecas analíticas
├── requirements-dev.txt      # Dependências de desenvolvimento e testes
└── README.md                 # Documentação completa do projeto
```

## 🚀 Como Executar

### 1. Preparação do Ambiente

Clone o repositório e configure o ambiente virtual:

```bash
# Clone o projeto
git clone https://github.com/seu-usuario/taxa-cancelamento-streaming.git
cd taxa-cancelamento-streaming

# Criação e ativação do ambiente virtual
python -m venv .venv
source .venv/bin/activate       # No Linux/macOS
# .venv\Scripts\activate        # No Windows
```

### 2. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 3. Inicialização do Painel

**Modo Padrão (carrega todas as seções):**

```bash
streamlit run taxa_de_cancelamento.py
```

**Modo Rápido / Lazy (renderiza apenas a aba ativa selecionada, recomendado para performance):**

```bash
# Linux / macOS:
PAINEL_NAVEGACAO=lazy streamlit run taxa_de_cancelamento.py

# Windows (PowerShell):
$env:PAINEL_NAVEGACAO="lazy"; streamlit run taxa_de_cancelamento.py

# Windows (CMD):
set PAINEL_NAVEGACAO=lazy && streamlit run taxa_de_cancelamento.py
```

Acesse a aplicação no navegador em `http://localhost`.

---

## 🧪 Executando Testes

Para rodar a suíte de testes unitários e de integração:

```bash
pip install -r requirements-dev.txt
pytest
```
