#!/usr/bin/env python3
# Agente2_DetectorCargaTributaria.py
# 2025 — Projeto IA2A
#
# Função:
#  - Calcular carga tributária por produto (pandas)
#  - Gerar ranking CSV + gráficos PNG
#  - Chamar a IA Gemma 3 (via Ollama) para análise profissional
#  - Gerar dashboard HTML com resultados e análises IA
#
# Como usar:
#  - Colocar este script na mesma pasta que planilha_original.xlsx
#  - Garantir Ollama + gemma3 baixado (ollama pull gemma3)
#  - Rodar: python Agente2_DetectorCargaTributaria.py

import os
import re
import subprocess
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import html

# -------------------------
# Configurações & nomes
# -------------------------
EXCEL_FILE = "planilha_original.xlsx"
OUTPUT_DIR = "output_carga_tributaria"
TOP_N = 10  # quantidade de produtos a enviar para análise IA
RUN_GEMMA = True  # definir False apenas para testar sem IA
GEMMA_MODEL_CMD = ["ollama", "run", "gemma3"]  # comando para chamar Gemma via Ollama

os.makedirs(OUTPUT_DIR, exist_ok=True)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M")

# Arquivos de saída
RANKING_CSV = os.path.join(OUTPUT_DIR, f"ranking_carga_tributaria_{ts}.csv")
CHART_PNG = os.path.join(OUTPUT_DIR, f"ranking_carga_tributaria_{ts}.png")
HIST_PNG = os.path.join(OUTPUT_DIR, f"hist_carga_tributaria_{ts}.png")
IA_REPORT_TOP = os.path.join(OUTPUT_DIR, f"analise_Gemma_carga_top{TOP_N}_{ts}.txt")
IA_REPORT_FULL = os.path.join(OUTPUT_DIR, f"analise_Gemma_carga_full_{ts}.txt")
DASHBOARD_HTML = os.path.join(OUTPUT_DIR, f"dashboard_carga_tributaria_{ts}.html")

# -------------------------
# Funções utilitárias
# -------------------------
def to_float_safe(x):
    """Converte vários formatos ('1.234,56', '12,5%', '—') para float; retorna 0.0 em erro."""
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == "" or s in ["—", "-", "–"]:
        return 0.0
    # remover R$, espaços
    s = s.replace("R$", "").replace(" ", "")
    # remover % só aqui se estiver usando; não assume porcentagem
    s = s.replace("%", "")
    # remover pontos de milhar (ex.: 1.234,56 -> 1234.56)
    s = re.sub(r"\.(?=\d{3}(?:\D|$))", "", s)
    s = s.replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

def pct_from_str_safe(x):
    """Converte '18%', '0.18', '18' para fração (ex.: 0.18)."""
    if pd.isna(x):
        return 0.0
    s = str(x).strip()
    if s == "" or s in ["—", "-", "–"]:
        return 0.0
    if "%" in s:
        return to_float_safe(s) / 100.0
    try:
        val = float(s.replace(",", "."))
        if 0 < val <= 1:
            return val
        if val > 1 and val <= 100:
            return val / 100.0
        return val
    except:
        return 0.0

def run_gemma(prompt_text: str, out_fname: str):
    """Chama Ollama Gemma3 via subprocess, envia prompt_text por stdin e grava stdout em out_fname."""
    print(f"\n🧠 [IA] Chamando Gemma 3 — gerando: {out_fname}  (isso pode demorar)...")
    with open(out_fname, "w", encoding="utf-8") as fout:
        process = subprocess.Popen(
            GEMMA_MODEL_CMD,
            stdin=subprocess.PIPE,
            stdout=fout,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = process.communicate(prompt_text, timeout=None)
        except Exception as e:
            process.kill()
            raise RuntimeError(f"Erro ao comunicar com Gemma: {e}")
        # se houver stderr, escrevemos ao final do arquivo para debug
        if stderr:
            fout.write("\n\n--- STDERR ---\n")
            fout.write(stderr)
    print(f"✅ [IA] Gemma finalizou e gravou: {out_fname}")

# -------------------------
# 1) Ler e validar planilha
# -------------------------
if not os.path.exists(EXCEL_FILE):
    raise FileNotFoundError(f"Arquivo não encontrado: {EXCEL_FILE}. Coloque o arquivo na pasta do script.")

print(f"📥 Lendo planilha: {EXCEL_FILE}")
df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
df.columns = [str(c).strip() for c in df.columns]

print("Colunas encontradas:", df.columns.tolist())

# -------------------------
# 2) Normalizar e extrair colunas relevantes
#    (com base no cabeçalho que você forneceu)
# -------------------------
# Colunas esperadas (conforme seu cabeçalho)
# NumeroNF, DataEmissao, CNPJFornecedor, RazaoSocial, ValorTotal, DescricaoItem, CFOP, CST, NCM,
# Quantidade, Unidade, UF, Municipio, ValorUnitario, NCM, ICMS (%), PIS/COFINS (%), ST, Monofásico, Observações

# Normalizar valores monetários e percentuais
if "ValorTotal" in df.columns:
    df["ValorTotal_num"] = df["ValorTotal"].apply(to_float_safe)
else:
    df["ValorTotal_num"] = 0.0

if "ValorUnitario" in df.columns:
    df["ValorUnitario_num"] = df["ValorUnitario"].apply(to_float_safe)
else:
    df["ValorUnitario_num"] = 0.0

if "Quantidade" in df.columns:
    df["Quantidade_num"] = df["Quantidade"].apply(to_float_safe)
else:
    df["Quantidade_num"] = 0.0

# Percentuais
if "ICMS (%)" in df.columns:
    df["_icms_pct"] = df["ICMS (%)"].apply(pct_from_str_safe)
else:
    df["_icms_pct"] = 0.0

# A sua planilha tem 'PIS/COFINS (%)' como uma coluna combinada
if "PIS/COFINS (%)" in df.columns:
    df["_pis_cofins_pct"] = df["PIS/COFINS (%)"].apply(pct_from_str_safe)
else:
    df["_pis_cofins_pct"] = 0.0

# ST (se informado em % ou em 'Sim/Não' — aqui tratamos se for percent)
if "ST" in df.columns:
    # se ST contiver % → converter; se contiver 'Sim'/'Não', tratamos como 0
    def st_to_frac(x):
        s = str(x).strip()
        if "%" in s:
            return pct_from_str_safe(s)
        return 0.0
    df["_st_pct"] = df["ST"].apply(st_to_frac)
else:
    df["_st_pct"] = 0.0

# Se houver coluna com valor de impostos já calculado (ex.: TotalImpostos), preferir
tax_amount_col = next((c for c in df.columns if re.search(r'imposto|tributo|impostos|tribu', c, re.IGNORECASE)), None)
if tax_amount_col:
    df["_tax_amount"] = df[tax_amount_col].apply(to_float_safe)
else:
    df["_tax_amount"] = 0.0

# -------------------------
# 3) Calcular receita estimada por linha e tributos estimados
# -------------------------
# regra: se ValorTotal_num disponível, usa; senão tenta ValorUnitario * Quantidade
df["_receita_estimada"] = df["ValorTotal_num"]
missing_revenue_mask = df["_receita_estimada"] == 0
df.loc[missing_revenue_mask, "_receita_estimada"] = (
    df.loc[missing_revenue_mask, "ValorUnitario_num"] * df.loc[missing_revenue_mask, "Quantidade_num"]
).fillna(0.0)

# tributos: se houver coluna de valor de imposto usa _tax_amount; senão soma % aplicadas sobre receita
df["_carga_pct"] = df[["_icms_pct", "_pis_cofins_pct", "_st_pct"]].sum(axis=1)
# se tax_amount presente e não zero, preferir valor; caso contrário, estimar por percentual
df["_tributos_estimados"] = df.apply(
    lambda r: r["_tax_amount"] if r["_tax_amount"] > 0 else r["_receita_estimada"] * r["_carga_pct"],
    axis=1
)

# -------------------------
# 4) Agregar por produto / descrição
# -------------------------
# Usar DescricaoItem como chave de agregação (fallback para NumeroNF se necessário)
agg_key = "DescricaoItem" if "DescricaoItem" in df.columns else df.columns[0]
group = df.groupby(agg_key).agg(
    receita_total=(" _receita_estimada" if False else "_receita_estimada", "sum"),
    tributos_total=("_tributos_estimados", "sum"),
    ocorrencias=("_receita_estimada", "count")
).reset_index()

# calcular carga por produto em %
group["carga_tributaria_pct"] = group.apply(
    lambda r: (r["tributos_total"] / r["receita_total"] * 100.0) if r["receita_total"] > 0 else 0.0,
    axis=1
)

# ordenar por carga percentual (peso) e também mostrar por valor absoluto
group = group.sort_values(by="carga_tributaria_pct", ascending=False)

# salvar ranking
group.rename(columns={agg_key: "DescricaoItem", "receita_total": "ReceitaTotal", "tributos_total": "TributosTotal"}, inplace=True)
group.to_csv(RANKING_CSV, index=False, encoding="utf-8-sig")
print(f"\n✅ Ranking gerado e salvo em: {RANKING_CSV}")

# -------------------------
# 5) Gerar gráficos
# -------------------------
# Top N por carga percentual
topn = group.head(TOP_N).copy()
plt.figure(figsize=(10, 6))
plt.barh(topn["DescricaoItem"].astype(str), topn["carga_tributaria_pct"], color="crimson")
plt.xlabel("Carga tributária (%)")
plt.title(f"Top {TOP_N} produtos por carga tributária (%)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(CHART_PNG)
plt.close()
print(f"✅ Gráfico (top {TOP_N}) salvo em: {CHART_PNG}")

# Histograma da distribuição de carga
plt.figure(figsize=(8, 4))
plt.hist(group["carga_tributaria_pct"].clip(0, 100), bins=20)
plt.xlabel("Carga tributária (%)")
plt.title("Distribuição de carga tributária por produto")
plt.tight_layout()
plt.savefig(HIST_PNG)
plt.close()
print(f"✅ Histograma salvo em: {HIST_PNG}")

# -------------------------
# 6) Preparar prompt para Gemma (amostra TOP_N + contexto)
# -------------------------
sample_text = topn[["DescricaoItem", "ReceitaTotal", "TributosTotal", "carga_tributaria_pct"]].to_string(index=False)

prompt_top = f"""
Você é uma inteligência fiscal especialista em tributação brasileira.
Análise de carga tributária por produto — relatório automático.

Contexto:
- Fonte: planilha_original.xlsx (processada por pandas).
- Objetivo: identificar produtos com maior peso de impostos e sugerir otimizações.

Amostra (top {TOP_N}) por carga tributária:
{sample_text}

Tarefas:
1) Indique as possíveis causas pelas quais esses produtos apresentam alta carga tributária.
2) Sugira 6 ações práticas e ordenadas por prioridade para reduzir carga tributária (ex.: revisão de NCM, verificação de CST/CFOP, regimes estaduais, revisão de preços, créditos fiscais).
3) Avalie riscos (fiscal, operacionais) ao aplicar cada ação.
4) Indique itens que necessitam revisão imediata e como auditar a procedência.
Responda em linguagem técnica porém objetiva, prepare um resumo executivo no final (3-5 linhas).
"""

prompt_full = f"""
Você é uma inteligência fiscal especialista em tributação brasileira.

Tenho o ranking completo de produtos com receita e tributos estimados (arquivo: {RANKING_CSV}).
Por favor:
1) Faça uma análise geral do perfil de carga tributária da base.
2) Aponte padrões (ex.: categorias com maior carga, presença de ST/Monofásico, CFOPs problemáticos).
3) Sugira roadmap de ações (curto, médio e longo prazo) para reduzir impacto fiscal.
4) Indique métricas e KPIs que a empresa deve monitorar para acompanhar evolução.

Responda em seções numeradas e finalize com um 'Resumo Executivo' curto.
"""

# -------------------------
# 7) Chamar Gemma para análise (TOP N e FULL)
# -------------------------
if RUN_GEMMA:
    run_gemma(prompt_top, IA_REPORT_TOP)
    run_gemma(prompt_full, IA_REPORT_FULL)
else:
    print("\n⚠️ RUN_GEMMA=False — pulando chamadas à IA. Para executar IA, defina RUN_GEMMA=True.\n")

# -------------------------
# 8) Montar dashboard HTML integrando tudo
# -------------------------
# Ler textos IA (se existirem) para embutir
ia_top_text = ""
ia_full_text = ""
if os.path.exists(IA_REPORT_TOP):
    with open(IA_REPORT_TOP, "r", encoding="utf-8") as f:
        ia_top_text = f.read()
if os.path.exists(IA_REPORT_FULL):
    with open(IA_REPORT_FULL, "r", encoding="utf-8") as f:
        ia_full_text = f.read()

# montar HTML
now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
group_html_table = group.head(200).to_html(index=False, classes="table", justify="left", border=0, escape=False)

html_page = f"""
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Dashboard — Detector de Carga Tributária</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:Arial,Helvetica,sans-serif;background:#f4f6f8;color:#111;margin:20px}}
.container{{max-width:1100px;margin:0 auto}}
.header{{display:flex;justify-content:space-between;align-items:center}}
.card{{background:#fff;padding:14px;border-radius:10px;box-shadow:0 4px 14px rgba(15,23,42,0.06);margin-bottom:12px}}
.kpi{{font-size:18px;font-weight:700}}
.small{{color:#6b7280}}
pre.ia{{background:#0b1220;color:#fff;padding:12px;border-radius:8px;white-space:pre-wrap;overflow:auto}}
.table-wrap{{background:#fff;padding:10px;border-radius:8px;box-shadow:0 2px 8px rgba(15,23,42,0.04);overflow:auto}}
.semaforo{{display:inline-block;padding:6px 10px;border-radius:6px;color:#fff;font-weight:700}}
.red{{background:#c0392b}}
.orange{{background:#f39c12}}
.green{{background:#27ae60}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>Detector de Carga Tributária — Projeto IA2A</h1>
      <div class="small">Gerado: {now} — IA envolvida: Gemma 3 (via Ollama)</div>
    </div>
  </div>

  <div class="card">
    <div class="kpi">Top {TOP_N} produtos por carga tributária (%)</div>
    <div class="small">Ranking salvo em: {RANKING_CSV}</div>
  </div>

  <div class="card">
    <img src="{CHART_PNG}" alt="Top carga tributaria" style="max-width:100%;height:auto;border-radius:6px">
  </div>

  <div class="card">
    <div class="kpi">Distribuição da carga tributária</div>
    <img src="{HIST_PNG}" alt="Histograma" style="max-width:100%;height:auto;border-radius:6px">
  </div>

  <div class="card">
    <h3>Análise IA — Top {TOP_N}</h3>
    <pre class="ia">{html.escape(ia_top_text) if ia_top_text else '(Análise IA não encontrada ou RUN_GEMMA=False)'}</pre>
  </div>

  <div class="card">
    <h3>Análise IA — Visão Geral & Roadmap</h3>
    <pre class="ia">{html.escape(ia_full_text) if ia_full_text else '(Análise IA não encontrada ou RUN_GEMMA=False)'}</pre>
  </div>

  <div class="card table-wrap">
    <h3>Tabela resumo (amostra)</h3>
    {group_html_table}
  </div>

  <div class="card">
    <small>Arquivos gerados: {RANKING_CSV}, {CHART_PNG}, {HIST_PNG}, {IA_REPORT_TOP if RUN_GEMMA else '(skip)'}, {IA_REPORT_FULL if RUN_GEMMA else '(skip)'}</small>
  </div>

</div>
</body>
</html>
"""

with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
    f.write(html_page)

print(f"\n✅ Dashboard final salvo em: {DASHBOARD_HTML}")
print("Abra o arquivo no navegador para visualizar resultados e análises da IA.")
