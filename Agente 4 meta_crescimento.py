import pandas as pd
from pathlib import Path

# === CONFIGURAÇÕES ===
pasta = Path(r"C:\Users\britt\Downloads\Projeto_Final_IA2A")
arquivo = pasta / "Dados_Nfe.xlsx"
saida = pasta / "simulacao_financeira.txt"

# PARÂMETROS DE CRESCIMENTO E CUSTOS
meta_crescimento_pct = 20       # Meta de crescimento em %
custo_fixo_anual = 180000       # Custo fixo anual em R$
custo_variavel_pct = 35         # Custo variável em %

# === LEITURA DA PLANILHA ===
df = pd.read_excel(arquivo, sheet_name="XLSX_NFE")
df.columns = [c.strip() for c in df.columns]

# === TRATAMENTO DA COLUNA VALORTOTAL ===
def tratar_valor(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except:
        return 0.0

df["ValorTotal"] = df["ValorTotal"].apply(tratar_valor)

# === CONVERSÃO DE DATAEMISSAO ===
df["DataEmissao"] = pd.to_datetime(df["DataEmissao"])

# === CALCULAR FATURAMENTO TOTAL DO PERÍODO DISPONÍVEL ===
faturamento_total = df["ValorTotal"].sum()
meses_unicos = df["DataEmissao"].dt.to_period("M").nunique()
faturamento_12_meses = faturamento_total * (12 / meses_unicos)

# === APLICAR META DE CRESCIMENTO ===
faturamento_com_meta = faturamento_12_meses * (1 + meta_crescimento_pct / 100)

# === CALCULAR CUSTOS ===
custo_variavel = faturamento_com_meta * (custo_variavel_pct / 100)
lucro_projetado = faturamento_com_meta - (custo_fixo_anual + custo_variavel)

# === EXIBIR RESULTADOS NO TERMINAL ===
print(f"📊 Faturamento base (12 meses): R$ {faturamento_12_meses:,.2f}")
print(f"📈 Faturamento com meta de {meta_crescimento_pct}%: R$ {faturamento_com_meta:,.2f}")
print(f"💸 Custo fixo anual: R$ {custo_fixo_anual:,.2f}")
print(f"💸 Custo variável ({custo_variavel_pct}%): R$ {custo_variavel:,.2f}")
print(f"📊 Lucro projetado: R$ {lucro_projetado:,.2f}")

# === SALVAR RESULTADO EM ARQUIVO TXT ===
with open(saida, "w", encoding="utf-8") as f:
    f.write(f"📊 Faturamento base (12 meses): R$ {faturamento_12_meses:,.2f}\n")
    f.write(f"📈 Faturamento com meta de {meta_crescimento_pct}%: R$ {faturamento_com_meta:,.2f}\n")
    f.write(f"💸 Custo fixo anual: R$ {custo_fixo_anual:,.2f}\n")
    f.write(f"💸 Custo variável ({custo_variavel_pct}%): R$ {custo_variavel:,.2f}\n")
    f.write(f"📊 Lucro projetado: R$ {lucro_projetado:,.2f}\n")

print(f"📁 Resultado salvo em: {saida}")
