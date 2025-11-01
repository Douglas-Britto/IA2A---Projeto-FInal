import os
import glob
import matplotlib.pyplot as plt
from langchain_community.llms import CTransformers
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# ================= CONFIGURAÇÕES =================
BASE_DIR = r"C:\Users\britt\Downloads\Projeto_Final_IA2A\agente_relatorio_final"
PAINEL_DIR = r"C:\Users\britt\Downloads\Projeto_Final_IA2A\output\painel_final"
MODEL_DIR = r"C:\Users\britt\modelos"  # pasta onde estão os modelos .gguf
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= FUNÇÕES AUXILIARES =================
def arquivo_recente(prefixo, pasta=PAINEL_DIR):
    arquivos = glob.glob(os.path.join(pasta, f"{prefixo}*"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo encontrado com prefixo '{prefixo}' em {pasta}")
    return max(arquivos, key=os.path.getctime)

def modelo_recente(pasta=MODEL_DIR):
    arquivos = glob.glob(os.path.join(pasta, "*.gguf"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum modelo .gguf encontrado em {pasta}")
    return max(arquivos, key=os.path.getctime)

# ================= ETAPA 1: CARREGAR ARQUIVOS =================
mercado_path = arquivo_recente("analise_mercado")
produtos_path = arquivo_recente("analise_produtos")
economia_path = arquivo_recente("analise_economia")
MODEL_PATH = modelo_recente()

print("📂 Arquivos encontrados:")
print(" - Mercado:", mercado_path)
print(" - Produtos:", produtos_path)
print(" - Economia:", economia_path)
print("📂 Modelo Gemma selecionado:", MODEL_PATH)

with open(mercado_path, 'r', encoding='utf-8') as f:
    texto_mercado = f.read()
with open(produtos_path, 'r', encoding='utf-8') as f:
    texto_produtos = f.read()
with open(economia_path, 'r', encoding='utf-8') as f:
    texto_economia = f.read()

# ================= ETAPA 2: GEMMA + LANGCHAIN =================
llm = CTransformers(
    model=MODEL_PATH,
    model_type="gemma",
    config={"max_new_tokens": 512, "temperature": 0.7}
)

template = PromptTemplate(
    input_variables=["mercado", "produtos", "economia"],
    template="""
Você é um analista de inteligência de mercado. Gere um relatório resumido com introdução, análise de mercado, análise de produtos e indicadores econômicos.

Dados de mercado:
{mercado}

Dados de produtos:
{produtos}

Dados econômicos:
{economia}
"""
)

chain = LLMChain(llm=llm, prompt=template)
resumo_final = chain.run({
    "mercado": texto_mercado,
    "produtos": texto_produtos,
    "economia": texto_economia
})

RESUMO_PATH = os.path.join(OUTPUT_DIR, 'relatorio_final.txt')
with open(RESUMO_PATH, 'w', encoding='utf-8') as f:
    f.write(resumo_final)

# ================= ETAPA 3: GERAR GRÁFICO =================
CHART_PATH = os.path.join(OUTPUT_DIR, 'chart.png')
labels = ['Mercado', 'Produtos', 'Economia']
valores = [len(texto_mercado.split()), len(texto_produtos.splitlines()), len(texto_economia.splitlines())]

plt.figure(figsize=(6,4))
plt.bar(labels, valores, color='darkblue')
plt.title('Volume de Dados por Seção')
plt.xlabel('Seções')
plt.ylabel('Quantidade')
plt.tight_layout()
plt.savefig(CHART_PATH)
plt.close()

print("✅ Resumo gerado:", RESUMO_PATH)
print("✅ Gráfico gerado:", CHART_PATH)
