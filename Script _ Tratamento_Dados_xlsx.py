import pandas as pd
import os

# Caminho do arquivo
caminho_pasta = r"C:\Users\britt\Downloads\IA2A - Projeto Final"
nome_arquivo = "IA2A Projeto Final - NFE.xlsx"
caminho_completo = os.path.join(caminho_pasta, nome_arquivo)

# Carregar o Excel
df = pd.read_excel(caminho_completo)

# Exibir as colunas disponíveis
print("📊 Colunas encontradas:")
print(df.columns)

# Somar os campos principais (ajuste os nomes conforme o seu arquivo)
soma_total = df["Valor Total"].sum()
soma_icms = df["Valor ICMS"].sum()
soma_impostos = df[["Valor ICMS", "Valor IPI", "Valor PIS", "Valor COFINS"]].sum().sum()

# Exibir os resultados
print("\n✅ Resultados:")
print(f"🔹 Somatório do Valor Total: R$ {soma_total:,.2f}")
print(f"🔹 Somatório do ICMS: R$ {soma_icms:,.2f}")
print(f"🔹 Carga Tributária Total (ICMS + IPI + PIS + COFINS): R$ {soma_impostos:,.2f}")
