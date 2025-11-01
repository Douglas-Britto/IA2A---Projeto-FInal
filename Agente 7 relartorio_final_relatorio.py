from chains.summarize_parts import resumir_mercado, resumir_produtos, resumir_economia
from chains.resumo_mercado import gerar_resumo_mercado
from chains.resumo_produtos import gerar_resumo_produtos
from chains.resumo_economia import gerar_resumo_economia
import os

def montar_relatorio_final():
   resumo_mercado = resumir_mercado(texto_mercado)
resumo_produtos = resumir_produtos(tabela_produtos)
resumo_economia = resumir_economia(tabela_economia)


    relatorio = f"""
==============================
RELATÓRIO FINAL - IA2A
==============================

{resumo_mercado}

{resumo_produtos}

{resumo_economia}
"""

    caminho_saida = r"C:\Users\britt\Downloads\Projeto_Final_IA2A\agente_relatorio_final\outputs\relatorio_final.txt"

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(relatorio)

    print("✅ Relatório final gerado com sucesso!")
    print(f"📄 Arquivo salvo em: {caminho_saida}")

# Executa a função
montar_relatorio_final()
