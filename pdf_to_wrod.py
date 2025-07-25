import pypandoc
import os


def converter_string_markdown_para_word(string_md, caminho_docx, caminho_modelo=None):
    """
    Converte uma string contendo Markdown para um documento Word (.docx)
    bem estruturado, usando Pandoc.

    Argumentos:
        string_md (str): A string com o conteúdo em formato Markdown.
        caminho_docx (str): O caminho onde o arquivo Word de saída será salvo.
        caminho_modelo (str, opcional): O caminho para um arquivo .docx de referência
                                        para usar como modelo de estilo.
    """
    print(f"Iniciando a conversão de string para '{caminho_docx}'...")

    # Prepara os argumentos extras, como o documento de referência para estilo
    extra_args = []
    if caminho_modelo:
        if os.path.exists(caminho_modelo):
            extra_args.append(f'--reference-doc={caminho_modelo}')
            print(f"Usando o modelo de estilo: '{caminho_modelo}'")
        else:
            print(f"AVISO: Arquivo de modelo '{caminho_modelo}' não encontrado. Usando estilo padrão.")

    try:
        # A função principal que converte o texto
        pypandoc.convert_text(
            source=string_md,
            to='docx',
            format='md',  # Essencial informar o formato de entrada
            outputfile=caminho_docx,
            extra_args=extra_args
        )

        print("Conversão concluída com sucesso!")
        print(f"Arquivo salvo em: {os.path.abspath(caminho_docx)}")

    except RuntimeError:
        print("ERRO: Pandoc não foi encontrado.")
        print("Por favor, instale o Pandoc no seu sistema e garanta que ele está no PATH.")
        print("Instruções: https://pandoc.org/installing.html")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# --- Exemplo de Uso ---

# 1. Defina sua string em Markdown
#    Usar aspas triplas (''' ou """) é ideal para strings com múltiplas linhas.
markdown_string_exemplo = '''
# Relatório Dinâmico de Vendas - 25/07/2025

## 1. Resumo Executivo

Este relatório foi gerado automaticamente às 12:18.
O conteúdo demonstra um crescimento consistente nas principais áreas de negócio.

## 2. Análise de Performance

A performance foi medida com base nos seguintes KPIs:

- **Novos Clientes:** Aumento de **22%**.
- **Receita Recorrente:** Crescimento de **17%**.
- *Nota: A análise de churn será detalhada na próxima seção.*

### 2.1. Tabela de Receita por Produto

| Produto      | Receita (em milhares) | Variação |
|--------------|-----------------------|----------|
| Produto A    | 450                   | +15%     |
| Produto B    | 320                   | +25%     |
| Produto C    | 150                   | +8%      |

Relatório gerado em: Fortaleza, Ceará.
'''

# 2. Defina os nomes dos arquivos de saída
arquivo_word_final_1 = 'relatorio_de_string_simples.docx'
arquivo_word_final_2 = 'relatorio_de_string_estilizado.docx'
modelo_de_estilo = 'modelo.docx'  # Lembre-se de criar este arquivo com seus estilos!

# 3. Execute a função

# Exemplo 1: Conversão simples, sem modelo de estilo
print("--- Executando conversão simples ---")
converter_string_markdown_para_word(markdown_string_exemplo, arquivo_word_final_1)

print("\n" + "=" * 40 + "\n")

# Exemplo 2: Conversão usando um modelo para definir a formatação
print("--- Executando conversão com modelo de estilo ---")
converter_string_markdown_para_word(markdown_string_exemplo, arquivo_word_final_2, caminho_modelo=modelo_de_estilo)