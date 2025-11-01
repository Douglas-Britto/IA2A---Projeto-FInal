import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# === CONFIGURAÇÕES DO TELEGRAM ===
TELEGRAM_TOKEN = "7577407381:AAHfwRDEadZrRtOPVjVQ9VOMaLJsA0Hq2do"
TELEGRAM_CHAT_ID = "5979800081"

# === DADOS EXTRAÍDOS DOS GRÁFICOS ===
faturamento_mensal = 74008.83
faturamento_quinzenal = 37004.42
faturamento_semanal = 17078.96
cmv_mensal = 33303.92
cmv_quinzenal = 16651.96

# === PARTE 1: GERAÇÃO DO RESUMO COM IA ===
llm = OllamaLLM(model="gemma3:4b")

template = f"""
Você é um analista financeiro experiente. Com base nos seguintes dados extraídos de gráficos:

- Faturamento projetado:
  - Mensal: R$ {faturamento_mensal:,.2f}
  - Quinzenal: R$ {faturamento_quinzenal:,.2f}
  - Semanal: R$ {faturamento_semanal:,.2f}

- CMV (Custo de Mercadoria Vendida) projetado:
  - Mensal: R$ {cmv_mensal:,.2f}
  - Quinzenal: R$ {cmv_quinzenal:,.2f}

Gere um resumo estratégico e inteligente com recomendações práticas e realistas para o empreendedor. Evite sugestões genéricas como “faça promoções” ou “poste nas redes sociais”.

O texto deve incluir:
1. Estratégias para alcançar o faturamento semanal, quinzenal e mensal.
2. Alertas sobre capital de giro com base no CMV.
3. Reflexões sobre preço de venda, fidelização de clientes e metas operacionais.
4. Tom profissional, direto e motivador.

Responda em português.
"""

prompt = PromptTemplate.from_template(template)
entrada = prompt.format()
resposta = llm.invoke(entrada)

# === PARTE 2: SALVAR RESUMO EM TXT ===
caminho_txt = os.path.join(os.path.dirname(__file__), "resumo_estrategico.txt")
with open(caminho_txt, "w", encoding="utf-8") as arquivo:
    arquivo.write(resposta)
print(f"\n📝 Resumo salvo em: {caminho_txt}")

# === PARTE 3: PRINT DA PASTA ===
pasta = os.path.dirname(os.path.abspath(__file__))
arquivos = os.listdir(pasta)

largura = 800
altura = 40 + 20 * len(arquivos)
imagem = Image.new("RGB", (largura, altura), color="white")
draw = ImageDraw.Draw(imagem)

try:
    fonte = ImageFont.truetype("arial.ttf", 16)
except:
    fonte = ImageFont.load_default()

draw.text((10, 10), "Arquivos na pasta do projeto:", fill="black", font=fonte)
for i, nome in enumerate(arquivos):
    draw.text((10, 40 + i * 20), f"- {nome}", fill="black", font=fonte)

imagem.save("print_pasta_projeto.png")
print("\n📸 Imagem gerada: print_pasta_projeto.png")

# === PARTE 4: ENVIO DE MENSAGEM VIA TELEGRAM COM REQUESTS ===
def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("📨 Mensagem enviada com sucesso via Telegram!")
    else:
        print("❌ Erro ao enviar mensagem:", response.text)

# Cálculo da meta diária
hoje = datetime.now().strftime("%d/%m/%Y")
meta_diaria = faturamento_mensal / 30
mensagem_telegram = (
    f"📆 {hoje}\n"
    f"🎯 Meta de vendas para hoje: R$ {meta_diaria:,.2f}\n"
    f"Se mantiver esse ritmo, você alcançará sua meta mensal de R$ {faturamento_mensal:,.2f}.\n"
    f"Foque nos clientes fiéis, ajuste preços com estratégia e mantenha o giro saudável!"
)

enviar_mensagem_telegram(mensagem_telegram)
