# Classificador_fiscal_Gemma.py

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# ⚡ LangChain + Ollama (Gemma 3:4b)
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# -------------------------------
# Configurações iniciais
# -------------------------------
CSV_FILE = "classificacao_fiscal_sugerida.csv"
GRAFICO_FILE = "grafico_inconsistencias_colorido.png"
DASHBOARD_FILE = "dashboard_fiscal_final.html"

# -------------------------------
# Ler CSV e consolidar divergências
# -------------------------------
df = pd.read_csv(CSV_FILE)

# Contagem de divergências
resumo_divergencias = {
    "CFOP": df["Divergência CFOP"].value_counts().get("Sim", 0),
    "CST": df["Divergência CST"].value_counts().get("Sim", 0),
    "NCM": df["Divergência NCM"].value_counts().get("Sim", 0)
}

# Produtos com qualquer divergência
produtos_divergentes = df[
    (df["Divergência CFOP"] == "Sim") |
    (df["Divergência CST"] == "Sim") |
    (df["Divergência NCM"] == "Sim")
]

# Preparar resumo textual para IA
resumo_textual = f"""
Resumo de divergências fiscais detectadas:

- CFOP: {resumo_divergencias['CFOP']} divergências
- CST: {resumo_divergencias['CST']} divergências
- NCM: {resumo_divergencias['NCM']} divergências

Total de produtos com qualquer divergência: {len(produtos_divergentes)}

Detalhes resumidos de produtos com divergência:
{produtos_divergentes[['NumeroNF','RazaoSocial','DescricaoItem','CFOP','CST','NCM','Divergência CFOP','Divergência CST','Divergência NCM']].to_string(index=False)}

Com base nessas informações, indique:
1. Principais problemas fiscais da empresa.
2. Recomendações de melhorias e ações prioritárias.
3. Explicação resumida e fácil para gestores.
"""

# -------------------------------
# Configurar LLM com Gemma 3:4b
# -------------------------------
llm = OllamaLLM(model="gemma3:4b")

template = PromptTemplate(
    input_variables=["resumo"],
    template="""
Você é um especialista fiscal. Analise o seguinte resumo de divergências e gere um relatório único de melhorias e recomendações para a empresa, indicando:
- Principais problemas
- Ações prioritárias
- Explicações simples para gestores
Responda em formato de texto corrido.

Resumo de divergências:
{resumo}
"""
)

chain = LLMChain(prompt=template, llm=llm)

# -------------------------------
# Gerar relatório da IA
# -------------------------------
relatorio_ia = chain.run(resumo=resumo_textual)

# Salvar relatório em TXT
nome_txt = f"relatorio_IA_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
with open(nome_txt, "w", encoding="utf-8") as f:
    f.write(relatorio_ia)

print(f"✅ Relatório IA gerado: {nome_txt}")

# -------------------------------
# Gerar dashboard HTML final
# -------------------------------
html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Fiscal Final</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
        .grafico {{ text-align: center; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Dashboard Fiscal Final</h1>

    <h2>📊 Gráfico de divergências</h2>
    <div class="grafico">
        <img src="{GRAFICO_FILE}" alt="Gráfico divergências" width="600">
    </div>

    <h2>📝 Relatório da IA - Recomendações</h2>
    <pre>{relatorio_ia}</pre>

    <h2>📋 Resumo de divergências</h2>
    <pre>{resumo_textual}</pre>
</body>
</html>
"""

with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Dashboard HTML final gerado: {DASHBOARD_FILE}")
