import pandas as pd
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from datetime import datetime
import os

# === 1. Diretório de saída ===
base_dir = r"C:\Users\britt\Downloads\Projeto_Final_IA2A\output"
output_dir = os.path.join(base_dir, "painel_final")
os.makedirs(output_dir, exist_ok=True)

# === 2. Indicadores econômicos reais via RAG Web ===
# Dados extraídos manualmente de fontes reais (Outubro 2025)
# Fonte: https://brasilindicadores.com.br/indicadores-economicos/painel-mensal-10-2025/

dados_economia = {
    "IPCA (%)": 5.12,
    "Selic (%)": 13.75,
    "INPC (%)": 4.89,
    "PIB (%)": 0.3,
    "Confiança do Consumidor": "Baixa"
}

df_economia = pd.DataFrame(list(dados_economia.items()), columns=["Indicador", "Valor"])

# === 3. Análise com IA Gemma 3 4B via LangChain ===
llm = Ollama(model="gemma3:4b", temperature=0.1)

prompt = PromptTemplate.from_template("""
Você é um analista econômico sênior. Com base nos indicadores abaixo, gere uma análise objetiva sobre o cenário econômico brasileiro em outubro de 2025, com foco em consumo, crédito e impacto no setor de informática.

Indicadores Econômicos:
{economia}

Responda em português, com linguagem profissional e traga números concretos para uso posterior em gráficos.
""")

entrada = prompt.format(economia=df_economia.to_string(index=False))
resposta = llm.invoke(entrada)

# === 4. Salvar análise e dados ===
nome_txt = f"analise_economia_ia_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
caminho_txt = os.path.join(output_dir, nome_txt)
df_economia.to_csv(os.path.join(output_dir, "dados_economia.csv"), index=False)

with open(caminho_txt, "w", encoding="utf-8") as f:
    f.write(resposta.strip())

print("✅ Indicadores econômicos coletados e analisados com IA.")
print(f"📄 Relatório salvo em: {caminho_txt}")
print("📊 Dados salvos em: dados_economia.csv")
