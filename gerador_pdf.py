import base64
from weasyprint import HTML, CSS

# --- 1. Logotipo da Empresa (SVG embutido em Base64 para não precisar de arquivo externo) ---
# Um logo genérico de exemplo
LOGO_SVG = """
<svg width="150" height="40" viewBox="0 0 150 40" xmlns="http://www.w3.org/2000/svg">
  <rect width="150" height="40" rx="5" fill="#0D47A1"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="white" font-weight="bold">
    INOVA
    <tspan fill="#BBDEFB" font-weight="normal">Corp</tspan>
  </text>
</svg>
"""
logo_base64 = base64.b64encode(LOGO_SVG.encode('utf-8')).decode('utf-8')
LOGO_DATA_URL = f"data:image/svg+xml;base64,{logo_base64}"

# --- 2. Conteúdo HTML do Relatório ---
# Adicionei mais texto para forçar a quebra de página e demonstrar o cabeçalho/rodapé
HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Corporativo – Q2 2025</title>
</head>
<body>
    <header class="title-page">
        <img src="{LOGO_DATA_URL}" alt="Logo da Empresa" class="logo">
        <h1>Relatório de Desempenho Corporativo</h1>
        <p class="subtitle">Análise Trimestral – Q2 2025</p>
        <div class="report-info">
            <p><strong>Empresa:</strong> Inova Corp S.A. – Filial Nordeste</p>
            <p><strong>Data de Emissão:</strong> 14 de Julho de 2025</p>
        </div>
    </header>

    <main>
        <h2>1. Sumário Executivo</h2>
        <p>O segundo trimestre de 2025 representou um período de <strong>crescimento consolidado e otimização estratégica</strong>. Superamos metas importantes de receita e aquisição de clientes, impulsionados pelo sucesso do novo produto "Conecta Mais". Este relatório detalha os KPIs, as conquistas, os desafios e estabelece as metas para o Q3 2025.</p>

        <h2>2. Análise de Desempenho (KPIs)</h2>
        <table>
            <thead>
                <tr>
                    <th>Indicador Chave (KPI)</th>
                    <th>Resultado Q1 2025</th>
                    <th>Resultado Q2 2025</th>
                    <th>Variação (%)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Receita Total</strong></td>
                    <td>R$ 450.000</td>
                    <td>R$ 520.000</td>
                    <td class="variation positive">▲ 15.6%</td>
                </tr>
                <tr>
                    <td><strong>Novos Clientes</strong></td>
                    <td>85</td>
                    <td>112</td>
                    <td class="variation positive">▲ 31.8%</td>
                </tr>
                <tr>
                    <td><strong>Taxa de Retenção</strong></td>
                    <td>92%</td>
                    <td>94%</td>
                    <td class="variation positive">▲ 2.2%</td>
                </tr>
                <tr>
                    <td><strong>Custo de Aquisição (CAC)</strong></td>
                    <td>R$ 1.250</td>
                    <td>R$ 1.100</td>
                    <td class="variation positive">▼ 12.0%</td>
                </tr>
                <tr>
                    <td><strong>Satisfação do Cliente (CSAT)</strong></td>
                    <td>8.8/10</td>
                    <td>8.5/10</td>
                    <td class="variation negative">▼ 3.4%</td>
                </tr>
            </tbody>
        </table>

        <h2>3. Análise Detalhada das Conquistas</h2>
        <p>O sucesso no trimestre não foi acidental. A estratégia de marketing digital focada em conteúdo de valor atraiu um público qualificado, resultando na melhoria do Custo de Aquisição de Clientes (CAC). Além disso, a expansão da equipe de vendas para o interior do estado provou ser uma decisão acertada, abrindo novos mercados promissores que não estavam sendo explorados.</p>
        <ul>
            <li><strong>Lançamento do Projeto "Horizonte Azul":</strong> A nova plataforma foi lançada com sucesso em maio, respondendo por 20% da nova receita.</li>
            <li><strong>Expansão da Equipe de Vendas:</strong> Contratação de 3 novos especialistas, permitindo uma cobertura mais ampla do mercado.</li>
            <li><strong>Reconhecimento da Mídia:</strong> Destaque no "Diário do Nordeste" como uma das empresas mais promissoras da região.</li>
        </ul>
        <p>Para o próximo trimestre, o foco será replicar esses sucessos enquanto mitigamos os desafios identificados, especialmente na área de satisfação do cliente, que apresentou uma leve queda devido ao aumento do volume de suporte.</p>

        <h2>4. Metas e Prioridades para o Q3 2025</h2>
        <ol>
            <li><strong>Recuperar o CSAT:</strong> Implementar plano de ação para o time de Sucesso do Cliente, com meta de atingir 9.0/10.</li>
            <li><strong>Crescimento Sustentável:</strong> Atingir uma receita de R$ 580.000, focando na venda de serviços de maior valor agregado.</li>
            <li><strong>Mitigação de Custos:</strong> Revisar contratos com fornecedores de logística para otimizar custos em pelo menos 5%.</li>
        </ol>
    </main>
</body>
</html>
"""

# --- 3. Estilo CSS Profissional ---
# Note o uso de @page para cabeçalhos e rodapés
CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');

/* --- Configurações Gerais da Página --- */
@page {
    size: A4;
    margin: 2cm 1.5cm 2.5cm 1.5cm; /* top, right, bottom, left */

    /* Conteúdo do cabeçalho */
    @top-center {
        content: "Inova Corp S.A. – Relatório Interno";
        font-family: 'Lato', sans-serif;
        font-size: 9pt;
        color: #777;
    }

    /* Conteúdo do rodapé com numeração */
    @bottom-right {
        content: "Página " counter(page) " de " counter(pages);
        font-family: 'Lato', sans-serif;
        font-size: 9pt;
        color: #777;
    }
}

/* --- Estilos do Corpo do Documento --- */
body {
    font-family: 'Lato', sans-serif;
    color: #333;
    font-size: 11pt;
    line-height: 1.5;
}

/* --- Página de Título (Primeira Página) --- */
.title-page {
    text-align: center;
    page-break-after: always; /* Força uma quebra de página após o título */
    height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.title-page .logo {
    margin-bottom: 40px;
}
.title-page h1 {
    font-size: 28pt;
    font-weight: 300;
    color: #0D47A1;
    margin: 0;
}
.title-page .subtitle {
    font-size: 16pt;
    font-weight: 300;
    color: #555;
    margin: 10px 0 40px 0;
}
.title-page .report-info p {
    font-size: 10pt;
    color: #666;
    margin: 5px 0;
}

/* --- Estilos do Conteúdo Principal --- */
main {
    counter-reset: h2-counter;
}
h2 {
    font-size: 18pt;
    font-weight: 700;
    color: #1A237E; /* Azul mais escuro */
    border-bottom: 2px solid #B0BEC5;
    padding-bottom: 8px;
    margin-top: 35px;
    margin-bottom: 20px;
    page-break-before: auto;
    page-break-after: avoid; /* Evita quebra de página logo após o título */
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    page-break-inside: avoid; /* Evita que a tabela seja quebrada */
}
th, td {
    border: 1px solid #CFD8DC;
    padding: 10px 12px;
}
th {
    background-color: #ECEFF1;
    font-weight: 700;
    color: #37474F;
    text-align: left;
}
td {
    text-align: center;
}

ul, ol {
    page-break-inside: avoid; /* Evita que listas sejam quebradas */
}
li {
    margin-bottom: 8px;
}

.variation.positive { color: #2E7D32; font-weight: bold; }
.variation.negative { color: #C62828; font-weight: bold; }
"""


# --- 4. Função para Gerar o PDF ---
def gerar_pdf_compativel(html_pdf:str,css_style:str,caminho_pdf:str):
    """Gera o relatório em PDF usando uma sintaxe compatível com versões antigas do WeasyPrint."""
    print("Iniciando a geração do relatório (modo de compatibilidade)...")

    try:
        html = HTML(string=html_pdf, base_url='.')
        css = CSS(string=css_style)

        output_filename = caminho_pdf

        # A chamada para write_pdf é simplificada, sem o argumento 'font_config'
        html.write_pdf(
            output_filename,
            stylesheets=[css]
        )

        print(f"✅ Sucesso! O arquivo '{output_filename}' foi gerado.")
        print("Este código foi ajustado para rodar em versões mais antigas do WeasyPrint.")

    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado durante a geração do PDF.")
        print(f"Detalhes do erro: {e}")


# --- Executa a função ---
if __name__ == "__main__":
    gerar_pdf_compativel(HTML_CONTENT,CSS_STYLE,'meu.pdf')