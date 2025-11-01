from pathlib import Path
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from datetime import datetime

# Caminho da pasta
PASTA = Path(r"C:\Users\britt\Downloads\Projeto_Final_IA2A")

# Leitura dos arquivos
contexto = PASTA.joinpath("contexto.txt").read_text(encoding="utf-8")
riscos = PASTA.joinpath("riscos.txt").read_text(encoding="utf-8")
oportunidades = PASTA.joinpath("oportunidades.txt").read_text(encoding="utf-8")

# Modelo Gemma via LangChain
llm = Ollama(model="gemma3:4b")



# Template do prompt
template = """
Você é um consultor fiscal especializado em legislação tributária brasileira.

Com base nos dados abaixo, elabore um parecer técnico com:
- Diagnóstico dos principais riscos fiscais
- Identificação das oportunidades tributárias
- Recomendações práticas para redução de carga tributária
- Tom consultivo, objetivo e profissional

{contexto}

Riscos Fiscais:
{riscos}

Oportunidades Tributárias:
{oportunidades}
"""

prompt = PromptTemplate(
    input_variables=["contexto", "riscos", "oportunidades"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)

# Execução
resposta = chain.run({
    "contexto": contexto,
    "riscos": riscos,
    "oportunidades": oportunidades
})

# Salvar relatório
RELATORIO = PASTA / "RelatorioFiscal_Gemma.txt"
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

cabecalho = f"{'='*60}\nRelatório Fiscal Inteligente\nGerado em: {timestamp}\n{'='*60}\n\n"
rodape = f"\n{'='*60}\nEste relatório foi gerado com IA (Gemma 3 4B via LangChain)\n{'='*60}\n"

RELATORIO.write_text(cabecalho + resposta + rodape, encoding="utf-8")
print("✅ Etapa 2 concluída: relatório gerado com sucesso!")
