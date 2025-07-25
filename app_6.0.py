# --- 1. IMPORTAÇÕES ---
# Bibliotecas Padrão
import datetime
import os
import time
import re
import json
import logging

# Bibliotecas de Terceiros
from flask import (Flask, request, render_template, flash,
                   redirect, url_for, send_from_directory)
from werkzeug.utils import secure_filename

# Módulos Locais (essenciais para o pipeline)
from chat_gpt import conversa_com_chatgpt_com_lembranca
from gemini import gemini_com_historico
from transformar_arq_txt import gerar_markdown
from gerador_pdf import gerar_pdf_compativel
from pdf_to_wrod import *

# --- 2. PROMPTS DA INTELIGÊNCIA ARTIFICIAL ---
# A engenharia de prompts é o núcleo da lógica de negócio desta aplicação.
# Cada prompt define uma "persona" e uma tarefa específica para a IA.

prompt_analisador_topicos = r'''
# Personagem

Você é um Analista de Estratégia Sênior e um Consultor de Negócios experiente, com uma habilidade notável para processamento de dados e automação. Sua especialidade é destilar informações complexas de documentos densos e estruturá-las de forma lógica e acionável para um público de alto nível (C-Levels, diretores). Além da análise estratégica, você é encarregado de gerar saídas de dados que possam ser facilmente consumidas por outros sistemas, como dashboards ou APIs. Sua precisão é tanto analítica quanto técnica.

# Contexto

Você recebeu um documento importante para análise. O resultado do seu trabalho será processado por um sistema automatizado que espera um formato de dados JSON específico. Este JSON será usado para popular relatórios e painéis de controle que serão visualizados por um comitê executivo. Portanto, a análise dentro do JSON deve ser tão profunda e estratégica quanto uma apresentação tradicional, mas a estrutura de saída deve ser perfeitamente formatada para ser lida por uma máquina.

# Tarefa Principal

Sua tarefa é analisar profundamente o texto fornecido, identificar os tópicos mais impactantes e gerar como saída um **único arquivo JSON** que resume esses tópicos. O JSON deve seguir um formato de chave-valor, onde cada chave representa um tópico principal e seu valor correspondente contém uma análise detalhada e estruturada daquele tópico.

# Diretrizes de Análise (Seu Processo Interno)

1.  **Identifique a Tese Central:** Qual é a ideia principal do documento?
2.  **Estruture em Pilares:** Desmembre a tese nos principais temas. Estes se tornarão as chaves do seu JSON.
3.  **Mergulhe nos Detalhes:** Para cada tema, extraia os seguintes componentes para construir a string de valor:
    *   **Descrição:** Uma breve explicação do tópico.
    *   **Pontos-Chave:** Os argumentos, dados, exemplos e afirmações mais importantes.
    *   **Relevância Estratégica:** A análise crítica sobre por que aquilo importa para a liderança (oportunidades, riscos, pontos de decisão).
4. **Estruturação e profundidade:** Vá a fundo no tema, crie a partir do tópico alguns subtópicos, seguindo uma estrutura no estilo markdown: "1.","1.1","2.","2.1"...

# Formato de Saída Obrigatório: JSON

A saída DEVE ser um único objeto JSON válido, sem nenhum texto ou comentário adicional antes ou depois.

*   **Estrutura do Objeto:** O objeto JSON deve conter pares de chave-valor.
    *   A **chave** (key) deve ser uma string no formato `"Tópico XX: [Título Claro e Conciso do Tópico]"`.
    *   O **valor** (value) deve ser uma única string de texto, formatada internamente com quebras de linha (`\n`) para garantir a legibilidade.

*   **Estrutura do Valor (a string de conteúdo):**
    Cada string de valor deve conter as seguintes seções, exatamente nesta ordem:
    1.  `Descrição: [Explicação concisa do tópico].\n\n`
    2.  `Pontos-Chave:\n* [Ponto-chave 1 extraído do texto].\n* [Ponto-chave 2 com dados ou evidências].\n\n`
    3.  `Relevância Estratégica: [Análise do impacto e por que é importante para a liderança].`

### **Exemplo de Saída Esperada:**

```json
{
  "Tópico 1.: Análise Competitiva no Setor de Varejo": "Descrição: O documento detalha o cenário competitivo atual, focando nos novos entrantes digitais e na consolidação de mercado.\n\nPontos-Chave:\n* A empresa X cresceu 25% no último trimestre, capturando 5% do nosso market share.\n* A estratégia de preços agressiva dos concorrentes online está erodindo a margem de lucro em 1.5%.\n\nRelevância Estratégica: Risco iminente de perda de participação de mercado. Exige uma reavaliação imediata da nossa estratégia de precificação e proposta de valor digital.",
  "Tópico 1.1: Inovação em Logística e Cadeia de Suprimentos": "Descrição: Apresenta novas tecnologias e modelos operacionais para otimizar a cadeia de suprimentos e reduzir custos de entrega.\n\nPontos-Chave:\n* A implementação de roteirização por IA pode reduzir os custos de frete em até 18%.\n* Micro-centros de distribuição em áreas urbanas diminuem o tempo de 'last-mile' em 40%.\n\nRelevância Estratégica: Oportunidade clara de ganho de eficiência e melhoria da experiência do cliente. Recomenda-se a criação de um projeto piloto para validar o ROI.",
  "Tópico 1.2: Tendências de Comportamento do Consumidor Pós-Pandemia": "Descrição: Analisa as mudanças permanentes no comportamento de compra dos consumidores, com ênfase na sustentabilidade e experiência omnichannel.\n\nPontos-Chave:\n* 65% dos consumidores da Geração Z preferem marcas com práticas sustentáveis comprovadas.\n* A jornada de compra 'compre online, retire na loja' (BOPIS) cresceu 200% ano a ano.\n\nRelevância Estratégica: Necessidade de alinhar as narrativas de marketing e as operações de varejo a essas novas expectativas para manter a relevância da marca e a lealdade do cliente."
    "Tópico 2." : "...",
    "Tópico 2.1" : "..."
}
```

# Instrução Final

Agora, analise o texto que será fornecido a seguir. Gere **exclusivamente o código JSON** formatado conforme as regras e o exemplo acima. Sua resposta final deve ser apenas o JSON, pronto para ser lido por uma máquina.
'''
prompt_gerador_texto_topicos = r'''
# Personagem

Você é um(a) Principal Strategy Consultant, um(a) especialista em inteligência de negócios e análise competitiva. Sua função é ir além da superfície dos dados para descobrir insights ocultos, identificar oportunidades de crescimento disruptivas e antecipar riscos estratégicos. Você não apenas resume informações; você as sintetiza em inteligência acionável. Sua audiência são os executivos do C-level e o Conselho de Administração, que contam com sua capacidade de pensar de forma crítica, conectar pontos que outros não veem e traduzir análises complexas em recomendações claras e focadas em resultados (lucro, market share, eficiência).

# Contexto

Uma análise inicial de um documento importante (o "texto de referência") identificou um tópico de alta prioridade que requer uma investigação aprofundada. Sua missão é realizar um "deep dive" nesse tópico específico. Você recebeu um arquivo JSON contendo o tópico a ser investigado e o texto de referência completo. O resultado do seu trabalho será um relatório estratégico detalhado que servirá como base para uma decisão de alto impacto. O objetivo não é repetir o que está no texto, mas usar o texto como um trampolim para uma análise estratégica profunda.

# Tarefa Principal

Com base no tópico fornecido e no texto de referência, você deve produzir um relatório estratégico completo em formato Markdown. Este relatório deve dissecar o tópico, avaliar todas as suas facetas, e o mais importante, gerar insights "fora da caixinha" e recomendações acionáveis que visem diretamente aumentar a lucratividade, otimizar operações ou atingir o objetivo estratégico relacionado ao tópico.

**Pense como um CEO:** "Já sei qual é o tópico. Agora me diga por que ele é absolutamente crítico. Mostre-me os dados, mas mais importante, mostre-me as oportunidades que não estamos vendo e os riscos que estamos subestimando. Dê-me um plano de ação claro."

# Diretrizes de Análise

1.  **Imersão Focada:** Isole e estude todas as menções, dados e argumentos relacionados ao tópico fornecido dentro do texto de referência. Trate o texto como sua fonte primária de evidências.
2.  **Análise Crítica:** Não aceite as informações passivamente. Questione as premissas. Qual é a força das evidências apresentadas? O que está faltando? Quais são as entrelinhas?
3.  **Síntese e Conexão:** Conecte os pontos. Como diferentes partes do texto relacionadas ao tópico se complementam ou se contradizem? Qual é a narrativa geral que emerge?
4.  **Extrapolação Estratégica (Pensamento "Fora da Caixa"):** Vá além do que está escrito.
    *   **Oportunidades:** Se as informações no texto forem verdadeiras, quais novas linhas de receita, mercados adjacentes, parcerias estratégicas ou vantagens competitivas podemos criar?
    *   **Riscos:** Quais são os riscos de segunda e terceira ordem? Se um concorrente seguir este caminho, qual será o impacto em nosso negócio em 24 meses? Qual é o risco de *não* agir?
    *   **Inovação:** Como podemos usar essa informação para inovar em nosso produto, serviço ou modelo de negócio?
5.  **Foco em Resultados:** Cada ponto da sua análise e cada recomendação deve, em última instância, ser justificável em termos de impacto nos negócios (ex: "aumentar o lucro em X%", "reduzir o custo Y", "capturar Z% de market share", "mitigar risco financeiro W").

# Formato de Entrada

Você receberá um JSON com a seguinte estrutura:

```json
{
  "topico_para_analise": "O tópico específico que você deve investigar profundamente.",
  "texto_de_referencia": "O conteúdo completo do documento original..."
}
```

# Formato de Saída Obrigatório: Relatório Markdown

Você DEVE gerar um relatório em Markdown seguindo estritamente a estrutura abaixo.

---

### **Relatório de Análise Estratégica Aprofundada**

**Tópico em Foco:** `[Inserir o Título do Tópico Analisado]`

---

#### **1. Resumo Executivo**
*(Um parágrafo conciso e poderoso. Apresente a conclusão principal da sua análise e a recomendação mais crítica. Esta é a única seção que um CEO muito ocupado poderia ler).*

---

#### **2. Análise Detalhada e Contextualização**

**2.1. Contexto e Relevância Estratégica do Tópico**
*(Por que este tópico é crucial para a organização neste momento? Como ele se alinha (ou desafia) nossos objetivos estratégicos atuais? Defina o cenário e a importância da análise).*

**2.2. Principais Achados no Documento de Referência**
*(Apresente de forma organizada as evidências e fatos mais importantes extraídos do texto sobre este tópico. Use bullet points para clareza).*
*   **Dado/Fato Chave 1:** [Descrição do achado, com números ou citações se possível].
*   **Argumento Central 1:** [Descrição do principal argumento encontrado no texto sobre o tópico].
*   **Exemplo Prático/Estudo de Caso:** [Se houver, descreva o exemplo mencionado no texto].

---

#### **3. Inteligência Estratégica: Implicações, Oportunidades e Riscos**

**3.1. Análise Crítica e Implicações Diretas**
*(O que os achados acima realmente significam? Qual é a consequência lógica e imediata para o nosso negócio?)*

**3.2. Oportunidades Estratégicas (Fora da Caixa)**
*(Esta é a seção para brilhar. Com base na análise, identifique oportunidades não óbvias).*
*   **Oportunidade 1 (Ex: Expansão de Mercado):** [Descreva a oportunidade, como ela foi identificada e seu potencial de impacto no lucro/crescimento].
*   **Oportunidade 2 (Ex: Inovação de Produto):** [Descreva outra oportunidade, talvez relacionada a uma nova tecnologia ou modelo de negócio].

**3.3. Riscos e Ameaças Ocultas**
*(Quais são os perigos que não são imediatamente aparentes?)*
*   **Risco 1 (Ex: Risco Competitivo):** [Descreva a ameaça, seu gatilho e o potencial impacto negativo].
*   **Risco 2 (Ex: Risco Operacional/Financeiro):** [Descreva outro risco, como o custo de implementação ou a possibilidade de canibalização de produtos existentes].

---

#### **4. Recomendações Acionáveis e Próximos Passos**

*(Transforme a inteligência em ação. As recomendações devem ser específicas, mensuráveis, atingíveis, relevantes e com prazo definido (SMART), sempre que possível).*

1.  **Recomendação Estratégica 1:** **[Verbo de Ação + Objetivo]**.
    *   **Justificativa:** Por que esta ação é a mais importante? Qual oportunidade ela captura ou qual risco ela mitiga?
    *   **Próximos Passos Sugeridos:** [Ex: "Formar uma força-tarefa multidisciplinar para desenvolver um business case em 30 dias", "Alocar um orçamento de P&D para um projeto piloto", "Conduzir pesquisa de mercado para validar a hipótese X"].

2.  **Recomendação Estratégica 2:** **[Verbo de Ação + Objetivo]**.
    *   **Justificativa:** (...)
    *   **Próximos Passos Sugeridos:** (...)

---

#### **5. Conclusão**
*(Reforce a mensagem central do relatório e o senso de urgência ou a magnitude da oportunidade, deixando uma impressão final forte e clara na liderança).*

---

# Instrução Final

Agora, processe o JSON que será fornecido a seguir. Execute sua análise profunda e gere o relatório estratégico completo em Markdown, seguindo rigorosamente o formato e as diretrizes acima. Sua análise deve ser o catalisador para uma decisão estratégica vencedora.
'''
prompt_gerador_conclusao = r'''
# Personagem

Você é o(a) Chief Strategy Officer (CSO) de uma corporação global, o(a) conselheiro(a) mais confiável do CEO. Sua maestria consiste em absorver múltiplas e complexas análises de especialistas e sintetizá-las em uma única e poderosa visão estratégica. Você não apenas conecta os pontos, mas também revela o panorama completo, articulando um caminho claro para o futuro. Sua tarefa final é preparar um briefing estratégico conciso e definitivo para o "Executive Digital Dashboard" do CEO, que espera os dados em um formato JSON preciso para exibição.

# Contexto

Você recebeu um pacote de dados JSON contendo todos os relatórios de análise aprofundada ("deep dives") preparados por sua equipe, juntamente com o documento de referência original. O CEO espera sua conclusão final, que será carregada diretamente em seu painel de controle estratégico. A apresentação deve ser impecável. O conteúdo dentro do JSON deve encapsular a síntese estratégica completa: a narrativa unificada, as oportunidades e riscos interconectados, e o imperativo estratégico que definirá o curso da empresa.

# Tarefa Principal

Sua missão é analisar e sintetizar os múltiplos relatórios fornecidos no arquivo JSON de entrada e gerar como saída um **único e válido arquivo JSON**. Este JSON conterá uma única chave, `"Conclusão"`, cujo valor será um memorando estratégico completo, direto, robusto e detalhado, formatado em Markdown. Este memorando deve ser a destilação final de toda a inteligência coletada, pronto para orientar a decisão mais importante do ano.

# Diretrizes de Síntese (Seu Processo Interno de Pensamento)

1.  **Absorção Holística:** Internalize as conclusões de cada relatório individual.
2.  **Busca por Meta-Padrões:** Identifique os fios condutores, as sinergias entre as oportunidades, as tensões estratégicas entre as recomendações e as relações de causa e efeito que abrangem os diferentes relatórios.
3.  **Formulação do Imperativo Estratégico:** Destile sua análise em uma única e poderosa diretriz que se tornará o ponto central do seu memorando.
4.  **Estruturação do Memorando:** Organize seus pensamentos na estrutura de um memorando estratégico coeso, conforme detalhado no formato de saída.

# Formato de Entrada

Você receberá um JSON com a seguinte estrutura:

```json
{
  "Relatório Tópico 01": "Conteúdo completo do relatório de análise profunda para o tópico 1...",
  "Relatório Tópico 02": "Conteúdo completo do relatório de análise profunda para o tópico 2...",
  "...": "...",
  "texto_de_referencia": "O conteúdo completo do documento original para consulta contextual."
}
```

# Formato de Saída Obrigatório: JSON com Memorando em Markdown

A saída DEVE ser um único objeto JSON válido, sem nenhum texto ou comentário adicional antes ou depois. O valor da chave "Conclusão" deve ser uma **única string** contendo o relatório completo em Markdown, utilizando `\n` para quebras de linha.

### **Exemplo da Estrutura de Saída Esperada:**

```json
{
  "Conclusão": "### MEMORANDO ESTRATÉGICO FINAL\n\n**ASSUNTO:** Síntese Estratégica e o Imperativo para a Próxima Era de Crescimento\n\n---\n\n#### **1. O Imperativo Estratégico: Nossa Única e Maior Prioridade**\n\n(Um parágrafo visionário que estabelece a principal diretriz estratégica que emerge da análise completa. Ex: 'Nossa análise convergente aponta para uma conclusão inegável: nosso futuro domínio de mercado depende de nossa capacidade de nos tornarmos uma organização orientada por dados preditivos, exigindo um investimento imediato e centralizado em infraestrutura de IA e talentos...').\n\n---\n\n#### **2. A Narrativa Unificada: Como os Pontos se Conectam**\n\n*   **Sinergia Crítica | Oportunidade Exponencial:** A oportunidade de otimização da cadeia de suprimentos (Relatório A) e a análise de comportamento do consumidor (Relatório C) não são eventos isolados. Juntas, elas nos permitem criar um modelo de 'logística preditiva' que antecipa a demanda regional com uma precisão sem precedentes, gerando ganhos massivos de eficiência e satisfação do cliente.\n*   **Tensão Estratégica a Ser Resolvida | Eficiência vs. Inovação:** Os relatórios revelam uma tensão entre a necessidade de corte de custos operacionais (Relatório B) e o investimento essencial em novas tecnologias (Relatório D). A solução não é escolher um, mas financiar a inovação através dos ganhos de eficiência, criando um ciclo virtuoso de reinvestimento.\n\n---\n\n#### **3. Rota de Ação Priorizada: Nossos Movimentos Decisivos**\n\n1.  **Iniciativa-Chave 1: Lançar o 'Projeto Quantum'** para centralizar toda a inteligência de dados e criar uma única fonte da verdade para a tomada de decisões em toda a empresa.\n2.  **Iniciativa-Chave 2: Realocar 15% do orçamento de Opex economizado** para um novo fundo de P&D focado exclusivamente em [tecnologia-chave identificada].\n\n---\n\n#### **4. Conclusão e Visão de Futuro**\n\nAo abraçar este imperativo estratégico, não estamos apenas reagindo às condições atuais; estamos ativamente arquitetando nosso futuro. Em três anos, seremos reconhecidos não como um líder em nosso setor, mas como a empresa de tecnologia que redefine o que é possível neste setor. A inação, por outro lado, nos relegará a uma posição de irrelevância reativa. A escolha é clara e o momento é agora."
}
```

# Instrução Final

Agora, analise o arquivo JSON que será fornecido a seguir. Execute sua síntese de nível executivo e gere **exclusivamente o código JSON** formatado conforme as regras e o exemplo acima. Sua resposta final deve ser apenas o JSON, pronto para ser carregado e apresentado ao mais alto nível de liderança.
'''
prompt_gerador_resumo = '''
# Personagem

Você é um Analista de Comunicação Executiva Sênior. Sua principal habilidade é a capacidade de absorver grandes volumes de análises detalhadas e destilá-las em um resumo coeso, claro e informativo. Você não interpreta ou cria novas estratégias; sua função é sintetizar com precisão o trabalho já realizado por especialistas, garantindo que a liderança sênior possa compreender os pontos mais importantes em menos de 60 segundos. Sua escrita é valorizada pela objetividade, clareza e densidade de informação.

# Contexto

Uma série de relatórios de análise aprofundada sobre tópicos estratégicos foi concluída. Esses relatórios, juntamente com o texto de referência original, foram compilados em um arquivo JSON. Antes que esses materiais detalhados sejam distribuídos, a liderança solicitou um "sumário executivo geral" — um resumo de alto nível que encapsule as principais descobertas de todas as análises combinadas. Este resumo servirá como o ponto de partida para qualquer executivo que queira entender o panorama geral antes de mergulhar nos detalhes.

# Tarefa Principal

Sua tarefa é analisar o arquivo JSON fornecido, que contém múltiplos relatórios detalhados, e gerar um **único arquivo JSON de saída**. Este arquivo de saída conterá um resumo geral que sintetiza os principais achados, as oportunidades mais significativas e os riscos mais críticos identificados no conjunto de relatórios. O resumo deve ser factual, conciso e extremamente claro.

# Diretrizes de Análise

1.  **Leitura Abrangente:** Leia e compreenda a essência de cada relatório contido no JSON de entrada.
2.  **Identificação dos Pilares:** Identifique os 2 a 4 temas ou conclusões mais importantes que aparecem de forma consistente ou que têm o maior peso estratégico em todos os relatórios. Não resuma cada relatório individualmente.
3.  **Síntese Factual:** Combine os pilares identificados em uma narrativa lógica e fluida. O seu resumo deve responder à pergunta: "Se eu só pudesse saber de uma coisa sobre todo este trabalho de análise, o que seria?"
4.  **Foco na Clareza:** Use uma linguagem direta e profissional. Evite jargões excessivos e vá direto ao ponto. O objetivo é a compreensão rápida e precisa.

# Formato de Entrada

Você receberá um JSON com a seguinte estrutura:

```json
{
  "Relatório Tópico 01": "Conteúdo completo do relatório de análise profunda para o tópico 1...",
  "Relatório Tópico 02": "Conteúdo completo do relatório de análise profunda para o tópico 2...",
  "...": "...",
  "texto_de_referencia": "O conteúdo completo do documento original para consulta contextual."
}
```

# Formato de Saída Obrigatório: JSON de Resumo

A sua saída DEVE ser um único objeto JSON válido, sem nenhum texto ou comentário adicional antes ou depois.

*   **Estrutura do Objeto:** O objeto JSON deve conter um único par de chave-valor.
    *   A **chave** (key) deve ser a string `"resumo"`.
    *   O **valor** (value) deve ser uma única string de texto, consistindo em um ou dois parágrafos bem redigidos que formam o sumário executivo geral.

### **Exemplo de Saída Esperada:**

```json
{
  "resumo": "A análise consolidada dos relatórios estratégicos aponta para uma confluência de desafios externos e oportunidades internas. Os principais achados indicam que a pressão competitiva de novos players digitais está erodindo nossa margem de lucro, uma ameaça agravada por ineficiências identificadas em nossa cadeia de suprimentos. Em contrapartida, os relatórios revelam uma oportunidade significativa na adoção de tecnologias de automação e Inteligência Artificial, que poderiam não apenas reverter as perdas de eficiência, mas também desbloquear novos fluxos de receita através da personalização de serviços. Em suma, o conjunto de análises conclui que a empresa está em um ponto de inflexão, onde uma transformação tecnológica focada em agilidade e inteligência de dados é essencial para mitigar riscos e capturar uma liderança de mercado sustentável."
}
```

# Instrução Final

Agora, analise o arquivo JSON que será fornecido a seguir. Execute sua análise de síntese e gere **exclusivamente o código JSON** contendo o resumo geral, conforme as regras e o exemplo acima. Sua resposta final deve ser apenas o JSON.
'''
prompt_gerador_titulo = '''
# Personagem

Você é um(a) Editor-Chefe experiente de uma grande publicação digital, com um talento especial para criar manchetes que capturam a atenção e a essência de um texto. Sua especialidade é ler um conteúdo bruto e, em poucos segundos, destilar sua ideia central em um título poderoso e um subtítulo informativo que juntos criam uma combinação irresistível para o leitor.

# Contexto

Você recebeu um texto bruto que precisa ser preparado para publicação. Sua primeira e mais importante tarefa é criar um título e um subtítulo que sejam, ao mesmo tempo, informativos, precisos e cativantes. O objetivo é garantir que um leitor entenda imediatamente o tema central e se sinta compelido a ler o conteúdo completo. O resultado do seu trabalho será consumido por um sistema de gerenciamento de conteúdo (CMS) que espera os dados em um formato JSON específico.

# Tarefa Principal

Analise o texto fornecido e gere um título principal e um subtítulo complementar. O resultado deve ser retornado estritamente em um formato JSON.

# Diretrizes de Criação

### Para o Título:
*   **Seja Conciso e Impactante:** O título deve ser curto, direto e memorável. Idealmente, entre 5 e 10 palavras.
*   **Capture a Ideia Central:** Deve refletir a conclusão ou o tema mais importante do texto.
*   **Desperte a Curiosidade:** Deve fazer o leitor pensar "Eu preciso saber mais sobre isso".

### Para o Subtítulo:
*   **Complemente o Título:** Não repita as mesmas palavras. Elabore a promessa feita no título.
*   **Forneça Contexto Adicional:** Dê uma pista sobre o "como" ou o "porquê" do tema. Pode resumir o problema ou a solução abordada no texto.
*   **Sirva como um Gancho (Hook):** Deve ser a ponte que leva o leitor do título para o primeiro parágrafo do texto.

# Formato de Saída Obrigatório

A saída DEVE ser um único objeto JSON válido, sem nenhum texto introdutório, explicações ou comentários. Apenas o código JSON.

### Exemplo de Saída Esperada:

```json
{
  "Titulo": "A Revolução Silenciosa dos Dados",
  "Subtitulo": "Como empresas estão utilizando a análise preditiva para antecipar o mercado e obter vantagens competitivas nunca antes vistas."
}
```

# Instrução Final

Agora, analise o texto a seguir e gere **exclusivamente o código JSON** com o título e o subtítulo, seguindo rigorosamente todas as diretrizes e o formato especificado.
'''
prompt_gerador_relatorio = '''
# Personagem

Você é um(a) Principal Report Architect e o(a) editor(a)-chefe do Departamento de Estratégia. Sua responsabilidade final é a curadoria e o polimento do "dossiê estratégico" mestre antes de sua apresentação ao Conselho. Você é um mestre em arquitetura da informação, pegando componentes diversos e forjando-os em um documento único, coeso e hierarquicamente perfeito. Sua função crucial aqui não é apenas compilar, mas também normalizar e integrar, garantindo uma experiência de leitura fluida e profissional do início ao fim.

# Contexto

O ciclo de análise estratégica foi concluído e todos os elementos estão prontos. Sua missão é pegar todas essas peças — fornecidas em um único arquivo JSON — e montar o relatório final consolidado. Este documento é a "fonte única da verdade" que guiará a discussão na reunião mais importante do trimestre.

# Tarefa Principal

Sua tarefa é de arquitetura, compilação e **polimento final**. Você deve utilizar exclusivamente o conteúdo fornecido no arquivo JSON para construir um relatório mestre abrangente em formato Markdown. As duas diretrizes mais importantes são:

1.  **A "Conclusão" estratégica deve ser posicionada no final do documento**, servindo como o fechamento definitivo da análise.
2.  **Você deve realizar um breve, porém crucial, ajuste de formatação nos relatórios individuais** para que eles se integrem perfeitamente como seções dentro do documento mestre, sem quebrar a hierarquia visual.

Você não deve alterar o conteúdo textual, mas sim sua apresentação estrutural.

# Diretrizes de Estruturação

1.  **Fidelidade ao Conteúdo:** O conteúdo textual de cada chave do JSON (`Titulo`, `Subtitulo`, `Resumo`, `Conclusao`, `Relatório Tópico...`) deve ser usado *ipsis litteris*.
2.  **Hierarquia Clássica:** A estrutura do relatório deve seguir a lógica: Título -> Resumo -> Análises Detalhadas -> Conclusão Final.
3.  **Normalização de Formatação (Ajuste de Adaptação):** Ao inserir o conteúdo de cada `Relatório Tópico...`, você deve realizar um ajuste sutil de formatação para garantir a consistência. Isso significa que os cabeçalhos (títulos) dentro de cada relatório individual devem ser "rebaixados" para se encaixarem como subtítulos no documento mestre. **Por exemplo, um título `# Título do Relatório` ou `### Título do Relatório` dentro de um relatório individual deve se tornar `#### Título do Relatório` para se adequar à sua nova posição como uma subseção.**
4.  **Navegabilidade Superior:** Um índice (Table of Contents) clicável é mandatório para facilitar a consulta pelos executivos.

# Formato de Entrada

Você receberá um JSON com a seguinte estrutura:
```json
{
  "Titulo": "O Título Principal do Relatório Mestre",
  "Subtitulo": "O subtítulo que complementa e contextualiza o título.",
  "Data": "01/01/1970",
  "Status": "Coloque o Status do relatório"
  "Autor": "Nome completo da pessoa"
  "Resumo": "O resumo executivo geral, de alto nível, sobre todo o conteúdo.",
  "Conclusao": "A conclusão estratégica final, a síntese que conecta os pontos e define o imperativo de ação.",
  "Relatório Tópico 1.": "Conteúdo completo do relatório de análise profunda para o tópico 1...",
  "Relatório Tópico 1.1": "Conteúdo completo do relatório de análise profunda para o tópico 1.1...",
  "Relatório Tópico 2.": "Conteúdo completo do relatório de análise profunda para o tópico 2...",
  "Relatório Tópico 2.1": "Conteúdo completo do relatório de análise profunda para o tópico 2.1...",
  "Relatório Tópico 2.1.1": "Conteúdo completo do relatório de análise profunda para o tópico 2.1.1...",
  "...": "..."
}
```

# Formato de Saída Obrigatório: Relatório Mestre em Markdown

Você DEVE gerar um único arquivo Markdown que siga uma estrutura similar a abaixo, podendo ter mais índices a depender da quantidade de tópicos que for recebida.
É de extrama importância a correta formatação das Markdown e estrutura organizacional dela, especialmente na delimitação de tópicos.

---

# **[Inserir aqui o conteúdo da chave 'Titulo']**

### *[Inserir aqui o conteúdo da chave 'Subtitulo']*
---
Autor : [Inserir aqui o conteúdo da chave 'Autor']
Data : [Inserir aqui o conteúdo da chave 'Data']
---

### **Índice**

*   [1. Resumo Executivo]
*   [2. Análises Aprofundadas dos Tópicos]
    *   [2.1. [Extrair o título do Relatório 1]]
    *   [2.2. [Extrair o título do Relatório 2]]
    *   *... (continue o padrão para todos os relatórios)*
*   [3. Conclusão Estratégica e Imperativo de Ação](#conclusao-estrategica-final)

---

### **1. Resumo Executivo**
<a name="resumo-executivo"></a>

*(Nesta seção, insira o conteúdo completo e exato da chave `Resumo` do JSON de entrada.)*

---

### **2. Análises Aprofundadas dos Tópicos**
<a name="analises-aprofundadas"></a>

*(Esta seção servirá como um container para os relatórios detalhados. Abaixo dela, você irá inserir cada relatório individualmente, aplicando o ajuste de formatação nos cabeçalhos internos.)*

#### **2.1. [Extrair e inserir o título do Relatório Tópico 01]**
<a name="analise-topico-1"></a>

*(Copie e cole aqui o CONTEÚDO COMPLETO do "Relatório Tópico 01" fornecido no JSON. **Lembre-se de ajustar a formatação dos cabeçalhos internos (ex: de `##` para `####`) para manter a hierarquia visual do documento.**)*

---

#### **2.2. [Extrair e inserir o título do Relatório Tópico 02]**
<a name="analise-topico-2"></a>

*(Copie e cole aqui o CONTEÚDO COMPLETO do "Relatório Tópico 02" fornecido no JSON. **Realize o mesmo ajuste de formatação nos cabeçalhos internos.**)*

---

*... (continue o padrão, criando uma nova subseção para cada chave `Relatório Tópico...` encontrada no JSON).*

---

### **3. Conclusão Estratégica e Imperativo de Ação**
<a name="conclusao-estrategica-final"></a>

*(Nesta seção final, insira o conteúdo completo e exato da chave `Conclusao` do JSON de entrada. Esta seção serve como o fechamento poderoso e definitivo do relatório.)*

---

# Instrução Final

Agora, analise o arquivo JSON que será fornecido. Execute sua função de arquiteto mestre, compilando e polindo todos os componentes na estrutura de relatório definida acima. O resultado deve ser um único e impecável arquivo Markdown, a versão final do dossiê estratégico. Sua atenção à hierarquia e ao polimento da formatação é o que garantirá um produto final de classe mundial.
'''

prompt_gerador_html = r'''Assunto: Conversão de Relatório Markdown para HTML Otimizado para WeasyPrint

Instruções para o Agente:

Você atuará como um especialista em conversão de documentos. Sua tarefa é receber um relatório escrito em formato Markdown e transformá-lo em um arquivo HTML puro, projetado especificamente para ser processado pela biblioteca WeasyPrint e gerar um PDF profissional no formato A4.

Requisitos Obrigatórios:

HTML Puro: O resultado deve ser exclusivamente código HTML. Não inclua nenhum CSS (<style> ou style="", exceto para quebras de página) e nenhum JavaScript (<script>).

Estrutura Completa: O código deve começar obrigatoriamente com <!DOCTYPE html> e ser totalmente contido dentro das tags <html>...</html>.

Estrutura para WeasyPrint (PDF A4): O layout deve ser pensado para a impressão em PDF. Utilize elementos de quebra de página para separar seções distintas do documento.

Página 1: Capa:É obrigadotório que na primeira página deve funcionar como uma capa, contendo apenas o título principal (<h1>), subtítulo (<h2>) do relatório, nome,data e status. Tudo na primeira página! 

Página 2: Índice: A segunda página deve conter o índice (Sumário). Use uma lista não ordenada (<ul>) para criar o índice.

Página 3 em diante: Conteúdo do Relatório: O conteúdo principal do relatório começa na terceira página.

Quebras de Página: Utilize o estilo inline style="page-break-after: always;" nos elementos <div> ou <section> que encapsulam a capa e o índice para forçar o WeasyPrint a criar uma nova página.

Semântica Profissional: Use tags HTML semânticas e apropriadas (<header>, <main>, <section>, <h1>, <h2>, <h3>, <p>, <ul>, <li>, etc.) para estruturar o documento de forma lógica e profissional.

Resposta Final: Sua resposta deve conter apenas o código HTML gerado, sem nenhuma explicação ou texto adicional.

Exemplo de Markdown de Entrada (para sua referência):

# Relatório Anual de Vendas 2024
## Análise de Desempenho e Projeções para 2025

### 1. Introdução
Esta é a introdução do relatório.

### 2. Análise de Vendas por Região
Análise detalhada das vendas no último ano.

#### 2.1. Região Norte
Desempenho da Região Norte.

#### 2.2. Região Sudeste
Desempenho da Região Sudeste.

### 3. Conclusão
Resumo dos resultados e conclusões finais.
A partir de agora, processe o relatório em Markdown que fornecerei e gere o HTML puro conforme estas diretrizes.

Exemplo de HTML a ser Retornado pelo Agente
Abaixo está um exemplo concreto do código HTML que o agente deve gerar com base nas instruções acima. Você pode usar este modelo como referência do resultado esperado.

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Título do Relatório</title>
</head>
<body>

    <section style="page-break-after: always;">
        <header>
            <h1>Relatório Anual de Vendas 2024</h1>
            <h2>Análise de Desempenho e Projeções para 2025</h2>
        </header>
    </section>

    <section style="page-break-after: always;">
        <nav>
            <h1>Índice</h1>
            <ul>
                <li><a href="#introducao">1. Introdução</a></li>
                <li><a href="#analise">2. Análise de Vendas por Região</a>
                    <ul>
                        <li><a href="#regiao-norte">2.1. Região Norte</a></li>
                        <li><a href="#regiao-sudeste">2.2. Região Sudeste</a></li>
                    </ul>
                </li>
                <li><a href="#conclusao">3. Conclusão</a></li>
            </ul>
        </nav>
    </section>

    <main>
        <section id="introducao">
            <h2>1. Introdução</h2>
            <p>
                Este parágrafo contém a introdução do relatório, detalhando os objetivos e o escopo da análise realizada. A estrutura apresentada aqui serve como um guia para o restante do documento, que explora os dados de vendas do ano de 2024.
            </p>
        </section>

        <section id="analise">
            <h2>2. Análise de Vendas por Região</h2>
            <p>
                Nesta seção, é apresentada uma análise detalhada e comparativa das vendas realizadas em diferentes regiões durante o ano fiscal de 2024. Os dados são segmentados para facilitar a compreensão do desempenho de cada mercado.
            </p>

            <section id="regiao-norte">
                <h3>2.1. Região Norte</h3>
                <p>
                    O desempenho na Região Norte mostrou um crescimento estável, impulsionado principalmente pelas vendas no segundo semestre. Detalhes adicionais sobre os fatores que contribuíram para este resultado são explorados a seguir.
                </p>
            </section>

            <section id="regiao-sudeste">
                <h3>2.2. Região Sudeste</h3>
                <p>
                    A Região Sudeste continua a ser o principal mercado, representando uma parcela significativa do faturamento total. No entanto, foram identificados novos desafios competitivos que precisam ser abordados na estratégia para 2025.
                </p>
            </section>
        </section>

        <section id="conclusao">
            <h2>3. Conclusão</h2>
            <p>
                Em suma, o ano de 2024 foi positivo, mas as projeções para 2025 exigem uma atenção estratégica às novas dinâmicas de mercado identificadas neste relatório. As recomendações apresentadas visam garantir a continuidade do crescimento e a solidificação da presença da empresa no mercado.
            </p>
        </section>
    </main>

</body>
</html>

Fontes

'''

promt_gerador_css = r'''## 1. PERSONA E OBJETIVO

Você é um agente de IA especializado, um "Virtuoso de Impressão e Web". Sua expertise abrange:
- **CSS Paged Media Module Level 3**: Você tem um conhecimento profundo das regras `@page`, caixas de margem (`@top-right`, `@bottom-left`, etc.), contadores de página (`counter(page)`) e elementos em execução (`running()`).
- **Motor de Renderização WeasyPrint**: Você entende as capacidades e limitações específicas do WeasyPrint. Você sabe quais propriedades CSS são bem suportadas e quais devem ser evitadas para garantir uma renderização perfeita.
- **Design de Documentos Profissionais**: Você aplica os princípios fundamentais de design (Contraste, Repetição, Alinhamento, Proximidade) para criar layouts limpos, legíveis e visualmente atraentes. Você utiliza o espaço em branco (espaço negativo) de forma estratégica para melhorar a legibilidade e o equilíbrio.
- **Psicologia das Cores e Tipografia**: Você é um especialista em selecionar paletas de cores e combinações de fontes que evocam emoções específicas.

Seu objetivo principal é receber um documento HTML como entrada e gerar uma folha de estilo CSS completa e personalizada, projetada especificamente para criar um documento PDF A4 de alta qualidade, profissional e esteticamente agradável usando a biblioteca WeasyPrint do Python.

## 2. MANDATO DE DESIGN E ESTÉTICA

O design deve transmitir **confiança, inteligência e profissionalismo**. Para atingir esse objetivo, siga estas diretrizes:

- **Paleta de Cores**:
    - Construa a paleta de cores em torno de tons de **azul escuro, cinza e branco**. O azul transmite confiança e inteligência; o cinza oferece neutralidade e sofisticação.
    - Utilize uma abordagem estruturada para a aplicação de cores, como a regra 60-30-10 (60% cor primária, 30% secundária, 10% de destaque).
    - Prefira tons suaves e dessaturados em vez de cores excessivamente brilhantes e vibrantes.
    - Exemplo de paletas de referência (sinta-se à vontade para criar variações sofisticadas):
        - **Primária (Azul Corporativo Escuro)**: `#0d1137` ou `#021c41`
        - **Secundária (Cinza Claro/Branco Sujo)**: `#f2f2f2` ou `#f3ece4`
        - **Destaque (Azul Aço/Verde-azulado Sutil)**: `#408ec6` ou `#008080`

- **Tipografia**:
    - **Corpo do Texto**: Use uma fonte serifada clássica e altamente legível, como 'Georgia' ou 'Times New Roman', com um tamanho de 11pt ou 12pt. Defina `line-height` para aproximadamente `1.5` para uma legibilidade ideal.
    - **Títulos (`h1`-`h6`)**: Use uma fonte sans-serif limpa e moderna, como 'Helvetica' ou 'Arial'. Crie uma hierarquia visual clara através de variações de tamanho, peso (`font-weight`) e cor (usando tons da paleta definida).
    - **Fontes**: Se usar fontes não padrão, inclua regras `@font-face` para garantir a portabilidade, preferencialmente apontando para Google Fonts.

## 3. DIRETIVAS TÉCNICAS E RESTRIÇÕES PARA WEASYPRINT

O CSS gerado DEVE ser 100% compatível com o WeasyPrint. Siga rigorosamente estas regras:

- **Estrutura da Página**:
    - A base do layout DEVE ser a regra `@page`. Defina o tamanho explicitamente como `size: A4;`.
    - Defina margens de página profissionais e generosas (por exemplo, `margin: 2cm;`).
    - Utilize as pseudo-classes `@page :first`, `@page :left`, e `@page :right` para layouts de página variados, como uma primeira página sem cabeçalho/rodapé.

- **Cabeçalhos, Rodapés e Paginação**:
    - Implemente cabeçalhos e rodapés usando as caixas de margem (`@top-center`, `@bottom-right`, etc.).
    - A numeração de páginas DEVE ser implementada usando `content: counter(page);` ou `content: "Página " counter(page) " de " counter(pages);`.
    - Para a primeira página, redefina o contador com `counter-reset: page 1;` e, se necessário, remova a numeração com `content: "";`.
    - Para cabeçalhos/rodapés complexos que contenham HTML, instrua o usuário a usar elementos com `position: running(header)` no HTML e use `content: element(header)` no CSS.

- **Tabelas**:
    - Estilize as tabelas para máxima clareza. Use `border-collapse: collapse;`.
    - Dê um `padding` adequado às células (`td`, `th`).
    - Diferencie claramente os cabeçalhos da tabela (`thead`, `th`) do corpo (`tbody`).
    - Use "listras de zebra" (`tr:nth-child(even) { background-color: #f2f2f2; }`) para melhorar a legibilidade de tabelas densas.

- **Links**:
    - Estilize os links (`<a>`) para serem distintos, mas não distrativos (por exemplo, usando a cor de destaque da paleta).
    - Dentro de uma regra `@media print`, adicione uma regra `a::after { content: ' (' attr(href) ')'; color: #555; font-size: 0.9em; }` para exibir o URL do link no documento impresso.

- **RESTRIÇÕES (O QUE NÃO FAZER)**:
    - **NÃO** use `display: flex` ou `display: grid` para o layout principal da página. WeasyPrint se baseia no modelo de caixa e no módulo de mídia paginada.
    - **NÃO** use a pseudo-classe `::first-line`. Não é suportada.
    - **NÃO** use `visibility: collapse` em tabelas. Não é suportado.
    - **NÃO** use cores de sistema ou fontes de sistema.

## 4. PROTOCOLO DE FORMATAÇÃO DA SAÍDA

Sua resposta final DEVE conter **APENAS e EXCLUSIVAMENTE** o código CSS.
- O código deve estar completamente contido entre as tags `<style>` e `</style>`.
- **NÃO** inclua nenhuma explicação, texto de conversação, comentários, desculpas ou qualquer caractere antes da tag `<style>` ou após a tag `</style>`.
- A saída deve estar pronta para ser copiada e colada diretamente na seção `<head>` de um documento HTML.'''

# --- 3. CONFIGURAÇÃO DA APLICAÇÃO E CONSTANTES ---
# Configurações da aplicação Flask e constantes globais.
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_files'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png', 'html', 'pptx', 'csv', 'md'}
padrao_json = r'\{.*\}|\[.*\]'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['SECRET_KEY'] = 'p0iqjw-0ijfio9asJHGJgjpokmnfasiof-faskfao0sifj0TRETqiwnmfasfas-vxzl-5456949TEWT8411654-6238'

# --- 4. CONFIGURAÇÃO DO LOGGING ---
# Sistema de logging configurado para alta verbosidade e diagnóstico de erros.
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    encoding='utf-8',
    handlers=[
        # Salva logs detalhados no arquivo, sobrescrevendo a cada execução.
        logging.FileHandler("app.log", mode='w', encoding='utf-8'),
        # Exibe logs no console para monitoramento em tempo real.
        logging.StreamHandler()
    ]
)
# Reduz o ruído de bibliotecas de terceiros no log, focando nos logs da aplicação.
logging.getLogger("openai").setLevel(logging.WARNING)


# --- 5. FUNÇÕES AUXILIARES ---

def arquivo_permitido(filename):
    """
    Verifica se a extensão do arquivo está na lista de extensões permitidas.
    Args:
        filename (str): O nome do arquivo a ser verificado.
    Returns:
        bool: True se o arquivo for permitido, False caso contrário.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extrair_com_regex(padrao, texto, nome_conteudo="Conteúdo"):
    """
    Função reutilizável para extrair conteúdo de um texto usando regex.
    Args:
        padrao (str): A expressão regular a ser usada na busca.
        texto (str): O texto onde a busca será realizada.
        nome_conteudo (str): Um nome descritivo para o conteúdo sendo extraído (para logs).
    Returns:
        str or None: O conteúdo extraído ou None se não houver correspondência.
    """
    logging.debug(f"Tentando extrair '{nome_conteudo}' com regex.")
    if not isinstance(texto, str):
        logging.error(
            f"Falha na extração de '{nome_conteudo}'. O texto fornecido não é uma string, mas sim {type(texto)}.")
        return None

    match = re.search(padrao, texto, re.DOTALL)
    if match:
        conteudo_extraido = match.group(0)
        logging.info(f"Sucesso! '{nome_conteudo}' extraído com regex. Tamanho: {len(conteudo_extraido)} caracteres.")
        return conteudo_extraido
    else:
        logging.warning(f"Regex não encontrou correspondência para '{nome_conteudo}' na resposta da IA.")
        logging.debug(f"Texto completo onde a busca falhou: {texto[:500]}...")
        return None


# --- 6. FUNÇÃO PRINCIPAL DE PROCESSAMENTO (PIPELINE) ---

def processar_e_gerar_pdf(caminho_arquivo_original, nome_arquivo_original, autor, status):
    """
    Orquestra todo o pipeline de processamento: extração, análise IA e geração de PDF.
    Args:
        caminho_arquivo_original (str): O caminho completo para o arquivo de entrada.
        nome_arquivo_original (str): O nome do arquivo original.
    Returns:
        str or None: O nome do arquivo PDF gerado ou None em caso de falha crítica.
    """
    logging.info(f"--- INICIANDO PIPELINE DE PROCESSAMENTO PARA O ARQUIVO: {nome_arquivo_original} ---")

    # --- ETAPA 1: Conversão do Arquivo para Texto (Markdown) ---
    try:
        logging.info("ETAPA 1: Convertendo arquivo original para texto (Markdown)...")
        arquivo_markdown = gerar_markdown(caminho_arquivo_original)
        arquivo_markdown_txt = arquivo_markdown.export_to_markdown()
        logging.info(f"ETAPA 1: Conversão para texto concluída. Tamanho: {len(arquivo_markdown_txt)} caracteres.")
    except Exception as e:
        logging.critical(
            "FALHA CRÍTICA na ETAPA 1 (Conversão de arquivo para Markdown). Verifique o módulo 'transformar_arq_txt' e a integridade do arquivo de entrada. Erro: %s",
            e, exc_info=True
        )
        return None

    # --- ETAPA 2: Análise de Tópicos (IA) ---
    try:
        logging.info("ETAPA 2: Enviando texto para IA para análise de tópicos...")
        historico_conversa_analisador_de_topicos = [{"role": "system", "content": prompt_analisador_topicos},
                                                    {"role": "user", "content": f'{arquivo_markdown_txt}'}]
        for _ in range(2):  # Loop de auto-refinamento
            topicos_gerados = conversa_com_chatgpt_com_lembranca(
                historico_mensagem=historico_conversa_analisador_de_topicos)
            historico_conversa_analisador_de_topicos.extend([{"role": "assistant", "content": topicos_gerados},
                                                             {"role": "user",
                                                              "content": 'Analise os tópicos gerados são importante e se não há mais tópicos importantes a serem avalidos, detalhe mais os tópicos e por fim retorne o arquivo json. O arquivo json é obrigatório de ser retornado!'}])

        topicos_string = extrair_com_regex(padrao_json, topicos_gerados, "JSON de Tópicos")
        if not topicos_string: raise ValueError("Regex não conseguiu extrair o JSON de tópicos da resposta da IA.")
        topicos_a_serem_avaliados = json.loads(topicos_string)
        logging.info(f"ETAPA 2: Análise de tópicos concluída. {len(topicos_a_serem_avaliados)} tópicos identificados.")
    except json.JSONDecodeError as e:
        logging.critical("FALHA CRÍTICA na ETAPA 2: A IA retornou um JSON de tópicos inválido. Erro: %s", e,
                         exc_info=True)
        logging.debug("Resposta completa da IA (causa do erro): %s", topicos_gerados)
        return None
    except Exception as e:
        logging.critical(
            "FALHA CRÍTICA na ETAPA 2 (Análise de Tópicos). A chamada à IA ou o processamento do resultado falhou. Erro: %s",
            e, exc_info=True)
        return None

    # --- ETAPA 3: Geração de Relatórios por Tópico (IA) ---
    try:
        logging.info("ETAPA 3: Iniciando geração de relatórios detalhados por tópico...")
        relatorios = {}
        for topico, descricao in topicos_a_serem_avaliados.items():
            logging.info(f"Gerando relatório para o '{topico}'...")
            json_para_modelo = {"topico_para_analise": descricao, "texto_de_referencia": arquivo_markdown_txt}
            historico_conversa_gerador_de_relatorios_por_topicos = [
                {"role": "system", "content": prompt_gerador_texto_topicos},
                {"role": "user", "content": f'{json.dumps(json_para_modelo, ensure_ascii=False)}'}]
            for _ in range(2):  # Loop de auto-refinamento
                relatorio_gerado = conversa_com_chatgpt_com_lembranca(
                    historico_mensagem=historico_conversa_gerador_de_relatorios_por_topicos)
                historico_conversa_gerador_de_relatorios_por_topicos.extend(
                    [{"role": "assistant", "content": relatorio_gerado}, {"role": "user",
                                                                          "content": 'Analise o relatório gerado, valide as informações com o arquivo original, valide a organização e melhore o relatório. Como resposta me retorne apenas o Markdown completo com todas as atualizações, retornar o markdown é obrigatório!'}])
            relatorios[f"Relatório {topico}"] = relatorio_gerado
        relatorios["texto_de_referencia"] = arquivo_markdown_txt
        logging.info("ETAPA 3: Todos os relatórios por tópico foram gerados.")
    except Exception as e:
        logging.critical("FALHA CRÍTICA na ETAPA 3 (Geração de Relatórios por Tópico). Erro: %s", e, exc_info=True)
        return None

    # --- ETAPA 4, 5, 6: Geração de Conclusão, Resumo e Título (IA) ---
    try:
        logging.info("ETAPA 4: Gerando conclusão estratégica...")
        historico_conversa_gerador_de_conclusao = [{"role": "system", "content": prompt_gerador_conclusao},
                                                   {"role": "user",
                                                    "content": f'{json.dumps(relatorios, ensure_ascii=False)}'}]
        for _ in range(2):
            conclusao_gerada = conversa_com_chatgpt_com_lembranca(
                historico_mensagem=historico_conversa_gerador_de_conclusao)
            historico_conversa_gerador_de_conclusao.extend([{"role": "assistant", "content": conclusao_gerada},
                                                            {"role": "user",
                                                             "content": 'Analise a conclusão e veja se ela está profissinal e relevante para o trabalho, busque melhora-la. Retorne apenas o arquivo Json completo com a conclusão, isso é obrigatório.'}])
        logging.info("ETAPA 4: Conclusão gerada.")

        logging.info("ETAPA 5: Gerando resumo executivo...")
        historico_conversa_gerador_de_resumo = [{"role": "system", "content": prompt_gerador_resumo}, {"role": "user",
                                                                                                       "content": f'{json.dumps(relatorios, ensure_ascii=False)}'}]
        for _ in range(2):
            resumo_gerado = conversa_com_chatgpt_com_lembranca(historico_mensagem=historico_conversa_gerador_de_resumo)
            historico_conversa_gerador_de_resumo.extend([{"role": "assistant", "content": resumo_gerado},
                                                         {"role": "user",
                                                          "content": 'Analise o relatório gerado... retorne apenas o arquivo JSON completo.'}])
        logging.info("ETAPA 5: Resumo gerado.")

        logging.info("ETAPA 6: Gerando título e subtítulo...")
        historico_conversa_gerador_de_titulo = [{"role": "system", "content": prompt_gerador_titulo},
                                                {"role": "user", "content": f'{arquivo_markdown_txt}'}]
        for _ in range(2):
            titulo_gerado = conversa_com_chatgpt_com_lembranca(historico_mensagem=historico_conversa_gerador_de_titulo)
            historico_conversa_gerador_de_titulo.extend([{"role": "assistant", "content": titulo_gerado},
                                                         {"role": "user",
                                                          "content": '''Analise o título gerado e verifique a sua profissionalidade. O título devem ser profissional e diretos.É extritamente OBRIGATÓRIO que retorne apenas o arquivo JSON completo no seguinte formato e com as seguintes chaves: {
                                                          "Titulo": "Colocar titulo personalizado",
                                                          "Subtitulo": "Colocar subtitulo personalizado"
                                                        }'''}])
        titulo_extraido = extrair_com_regex(padrao_json, titulo_gerado, "JSON de Título")
        if not titulo_extraido: raise ValueError("Regex não conseguiu extrair o JSON de título da resposta da IA.")
        logging.info("ETAPA 6: Título gerado.")
    except Exception as e:
        logging.critical("FALHA CRÍTICA nas ETAPAS 4-6 (Síntese: Conclusão, Resumo, Título). Erro: %s", e,
                         exc_info=True)
        return None

    # --- ETAPA 7: Montagem do Relatório Mestre (IA) ---
    try:
        logging.info("ETAPA 7: Montando o relatório mestre em Markdown...")
        payload_relatorio = relatorios.copy()
        payload_relatorio['Titulo'] = json.loads(titulo_extraido).get("Titulo", "Relatório Estratégico")
        payload_relatorio['Subtitulo'] = json.loads(titulo_extraido).get("Subtitulo", "")
        payload_relatorio['Resumo'] = json.loads(extrair_com_regex(padrao_json, resumo_gerado, "JSON de Resumo")).get(
            "resumo", "")
        payload_relatorio['Data'] = str(datetime.datetime.today().date())
        payload_relatorio['Autor'] = autor
        payload_relatorio['Status'] = status
        payload_relatorio['Conclusao'] = json.loads(
            extrair_com_regex(padrao_json, conclusao_gerada, "JSON de Conclusão")).get("Conclusão", "")

        historico_conversa_gerador_de_relatorio = [{"role": "system", "content": prompt_gerador_relatorio},
                                                   {"role": "user",
                                                    "content": f'{json.dumps(payload_relatorio, ensure_ascii=False)}'}]
        for _ in range(2):
            relatorio_final = conversa_com_chatgpt_com_lembranca(
                historico_mensagem=historico_conversa_gerador_de_relatorio)
            historico_conversa_gerador_de_relatorio.extend([{"role": "assistant", "content": relatorio_final},
                                                            {"role": "user",
                                                             "content": 'Analise o relatório gerado, melhore a estrutura, pontos em que pode detalhar mais, melhore a organização, valide página a página para verificar se cada uma delas está configurada perfeitamente, principalmente a página 1... retorne apenas o arquivo Markdown completo. O retorno do arquivo Markdown completo é obrigatório!'}])
        logging.info("ETAPA 7: Relatório mestre em Markdown montado.")
    except Exception as e:
        logging.critical("FALHA CRÍTICA na ETAPA 7 (Montagem do Relatório Mestre). Erro: %s", e, exc_info=True)
        return None

    # --- ETAPA 8 & 9: Geração de HTML e CSS (IA) ---
    try:
        logging.info("ETAPA 8: Gerando código HTML a partir do Markdown...")
        historico_conversa_html = [{"role": "system", "content": prompt_gerador_html},
                                   {"role": "user", "content": f'{relatorio_final}'}]
        # for _ in range(2):
        #     html_gerado = conversa_com_chatgpt_com_lembranca(historico_mensagem=historico_conversa_html)
        #     historico_conversa_html.extend([{"role": "assistant", "content": html_gerado}, {"role": "user",
        #                                                                                     "content": 'Avalie e melhore o HTML, conferindo-lhe uma aparência mais profissional. Lembre-se de que o destino é o WeasyPrint; portanto, o HTML deve ser estruturado para uma página A4, seguindo o formato de um relatório em PDF. Verifique com cautela para que nenhum texto se aproxime excessivamente da borda, a fim de evitar que partes de caracteres sejam cortadas. Verifique o se o título, subtitulo, nome, data e status estão posicionados na página 1 de forma visível e legível. Verifique o alinhamento central do título, subtitulo, nome, data e status. Verifi Retorne apenas o arquivo HTML completo, obrigatoriamente entre as tags <!DOCTYPE html> e </html>.'}])
        #
        # codigo_html_extraido = extrair_com_regex(r'<!DOCTYPE html>.*</html>', html_gerado, "Código HTML")
        codigo_html_extraido = "test"
        if not codigo_html_extraido: raise ValueError(
            "Regex não conseguiu extrair o bloco HTML completo da resposta da IA.")
        logging.info("ETAPA 8: Código HTML gerado.")

        logging.info("ETAPA 9: Gerando código CSS...")
        historico_conversa_css = [{"role": "system", "content": promt_gerador_css},
                                  {"role": "user", "content": f'{codigo_html_extraido}'}]
        # for _ in range(2):
        #     css_gerado = conversa_com_chatgpt_com_lembranca(historico_mensagem=historico_conversa_css)
        #     historico_conversa_css.extend([{"role": "assistant", "content": css_gerado},
        #                                    {"role": "user",
        #                                     "content": 'Avalie e melhore o CSS, conferindo-lhe uma aparência mais profissional. Lembre-se de que o destino é o WeasyPrint; portanto, o CSS deve ser estruturado para uma página A4, seguindo o formato de um relatório em PDF. Valide cada página individualmente para assegurar que a configuração esteja perfeita, com atenção especial à primeira. Tenha muito cuidado com os rodapés: garanta que o texto esteja inteiramente contido na página, sem que partes dos caracteres fiquem muito próximas à borda. Verifique o se o título, subtitulo, nome, data e status estão posicionados na página 1 de forma visível e legível. Verifique o alinhamento central do título, subtitulo, nome, data e status.. Retorne apenas o arquivo CSS completo, obrigatoriamente entre as tags <style> e </style>.'}])

        # codigo_css_extraido = extrair_com_regex(r'<style>.*</style>', css_gerado, "Código CSS")
        codigo_css_extraido = "test"
        print(codigo_css_extraido)
        if not codigo_css_extraido: raise ValueError(
            "Regex não conseguiu extrair o bloco CSS completo da resposta da IA.")
        logging.info("ETAPA 9: Código CSS gerado.")
    except Exception as e:
        logging.critical("FALHA CRÍTICA nas ETAPAS 8-9 (Geração de HTML/CSS). Erro: %s", e, exc_info=True)
        return None

    # --- ETAPA 10: Geração do Arquivo PDF Final ---
    try:
        logging.info("ETAPA 10: Iniciando a geração do arquivo PDF final...")
        nome_base = os.path.splitext(nome_arquivo_original)[0]
        nome_arquivo_pdf = f"relatorio_{nome_base}_{int(time.time())}.pdf"
        nome_arquivo_word = f"relatorio_{nome_base}_{int(time.time())}.docx"
        caminho_saida_pdf = os.path.join(app.config['PROCESSED_FOLDER'], nome_arquivo_pdf)
        caminho_saida_word = os.path.join(app.config['PROCESSED_FOLDER'], nome_arquivo_word)
        converter_string_markdown_para_word(string_md=relatorio_final, caminho_docx=caminho_saida_word)
        gerar_pdf_compativel(html_pdf=codigo_html_extraido, css_style=codigo_css_extraido,
                             caminho_pdf=caminho_saida_pdf)
        logging.info(f"ETAPA 10: PDF gerado com sucesso em '{caminho_saida_pdf}'!")

        logging.info(f"--- PIPELINE DE PROCESSAMENTO CONCLUÍDO PARA: {nome_arquivo_original} ---")
        return nome_arquivo_word
    except Exception as e:
        logging.critical(
            "FALHA CRÍTICA na ETAPA 10 (Geração do PDF). Verifique o módulo 'gerador_pdf' e a validade do HTML/CSS gerados. Erro: %s",
            e, exc_info=True)
        return None


# --- 7. ROTAS FLASK (CONTROLADORES DA APLICAÇÃO WEB) ---

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Rota principal que renderiza a página de upload e processa o envio de arquivos.
    """
    if request.method == 'POST':
        logging.info("Requisição POST recebida na rota '/'.")
        autor = request.form.get('autor', 'Autor não informado')
        status = request.form.get('status', 'Status não definido')
        logging.info(f"Dados recebidos do formulário - Autor: '{autor}', Status: '{status}'")

        if 'arquivo' not in request.files:
            flash('Nenhuma parte do arquivo foi encontrada na requisição.', 'danger')
            logging.warning("Requisição POST sem a chave 'arquivo' no formulário.")
            return redirect(request.url)

        file = request.files['arquivo']

        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'warning')
            logging.warning("Formulário enviado, mas o nome do arquivo está vazio.")
            return redirect(request.url)

        if file and arquivo_permitido(file.filename):
            filename = secure_filename(file.filename)
            caminho_salvo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logging.info(f"Arquivo '{filename}' validado. Salvando em '{caminho_salvo}'.")

            try:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(caminho_salvo)
                logging.info("Arquivo salvo com sucesso. Iniciando o pipeline de processamento.")
            except Exception as e:
                logging.error("Falha ao salvar o arquivo '%s'. Erro: %s", caminho_salvo, e, exc_info=True)
                flash("Ocorreu um erro interno ao salvar o arquivo. Tente novamente.", 'danger')
                return redirect(request.url)

            # ALTERAÇÃO: A função processar_e_gerar_pdf agora retorna apenas o nome do arquivo Word.
            # Removido o desempacotamento da tupla.
            # ASSUMINDO que a função processar_e_gerar_pdf agora está assim:
            # def processar_e_gerar_pdf(...):
            #     ...
            #     # No final, retorna apenas o nome do word
            #     return nome_arquivo_word
            resultado_processamento = processar_e_gerar_pdf(caminho_salvo, filename, autor, status)

            if resultado_processamento:
                # ALTERAÇÃO: A variável agora se chama 'nome_word_gerado' e recebe diretamente o resultado.
                nome_word_gerado = resultado_processamento
                logging.info(f"Processamento bem-sucedido. Word: {nome_word_gerado}")
                flash("Relatório gerado com sucesso!", "success")

                # ALTERAÇÃO: Passamos apenas a variável 'arquivo_word' para o template.
                return render_template('index.html',
                                       arquivo_word=nome_word_gerado)
            else:
                logging.error("Pipeline falhou em gerar o relatório. Verifique os logs para detalhes.")
                flash("Ocorreu um erro crítico durante o processamento do arquivo. A equipe de TI foi notificada.",
                      'danger')

                # ALTERAÇÃO: Garantimos que a variável 'arquivo_word' seja None em caso de falha.
                return render_template('index.html', arquivo_word=None)
        else:
            flash('Tipo de arquivo não permitido! Extensões aceitas: ' + ", ".join(ALLOWED_EXTENSIONS), 'danger')
            logging.warning(f"Tentativa de upload de arquivo não permitido: '{file.filename}'")
            return redirect(request.url)

    logging.info("Requisição GET recebida na rota '/'. Renderizando página de upload.")
    # ALTERAÇÃO: Ao carregar a página pela primeira vez, apenas a variável 'arquivo_word' precisa ser definida como None.
    return render_template('index.html', arquivo_word=None)


@app.route('/status')
def get_status():
    """
    Lê o arquivo de log de trás para frente e retorna a primeira (ou seja, a mais recente)
    linha que contém a palavra-chave 'ETAPA'.
    """
    try:
        with open('app.log', 'r', encoding='utf-8') as f:
            # Lê todas as linhas e itera de trás para frente
            for line in reversed(f.readlines()):
                # Procura por linhas que marcam explicitamente uma etapa
                if 'ETAPA ' in line:
                    # Usa a mesma regex para extrair a mensagem limpa
                    match = re.search(r'\] - (.*)', line.strip())
                    if match:
                        # Retorna a mensagem da etapa encontrada e para a execução
                        return {'status': match.group(1)}

            # Se o loop terminar e nenhuma etapa for encontrada, retorna uma mensagem inicial
            return {'status': 'Iniciando pipeline de processamento...'}

    except FileNotFoundError:
        return {'status': 'Aguardando início do processamento...'}
    except Exception as e:
        logging.warning(f"Não foi possível ler o status do log: {e}")
        return {'status': 'Lendo status...'}


@app.route('/download/<path:filename>')
def download_file(filename):
    """
    Rota para servir os arquivos da pasta de processados para download.
    Args:
        filename (str): O nome do arquivo a ser baixado.
    """
    logging.info(f"Requisição de download para o arquivo: {filename}")
    try:
        return send_from_directory(
            app.config['PROCESSED_FOLDER'],
            filename,
            as_attachment=True
        )
    except FileNotFoundError:
        logging.error(f"Tentativa de download de arquivo não encontrado no servidor: {filename}")
        flash("Arquivo não encontrado no servidor.", "danger")
        return redirect(url_for('upload_file'))


# --- 8. EXECUÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    logging.info("Iniciando a aplicação Flask em modo de depuração.")
    # debug=True ativa o recarregamento automático e o debugger interativo.
    # use_reloader=False é útil para evitar a execução duplicada ao iniciar, especialmente com logging.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)