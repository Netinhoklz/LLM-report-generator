# Gerador de Relatórios Estratégicos com IA

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uma aplicação Flask inteligente que transforma documentos brutos (PDF, DOCX, PPTX, etc.) em relatórios estratégicos profissionais e estruturados, utilizando um sofisticado pipeline de Inteligência Artificial em múltiplas etapas.

### Demonstração


graph TD
    A[Start: Usuário Acessa a Página] --> B{Envia Arquivo, Autor e Status};
    B --> C[Backend: Flask Recebe a Requisição];
    C --> D{Arquivo é Válido?};
    D -- Não --> E[Flash: Erro de Tipo de Arquivo];
    E --> A;
    D -- Sim --> F[Arquivo salvo em /uploads];
    F --> G[**Início do Pipeline de IA**];

    subgraph "Pipeline de Processamento (processar_e_gerar_pdf)"
        G --> H[1. Converter Arquivo Original para Texto (Markdown)];
        H --> I[2. IA Analisa Texto e Extrai Tópicos (JSON)];
        I --> J[3. IA Gera Relatórios Detalhados para cada Tópico];
        J --> K[4. IA Sintetiza os Relatórios<br/>(Cria Conclusão, Resumo e Título)];
        K --> L[5. IA Monta o Relatório Mestre Final (Markdown)];
        L --> M[6. Gerar Arquivo de Saída .docx];
    end

    M --> N{Processamento Bem-Sucedido?};
    N -- Não --> O[Flash: Erro Crítico no Processamento];
    N -- Sim --> P[Flash: Sucesso! Relatório Gerado];
    O --> Q[Frontend: Renderiza a Página sem Link de Download];
    P --> R[Frontend: Renderiza a Página com Botão de Download para o .docx];
    R --> S[Usuário clica em 'Baixar Word'];
    S --> T[Backend: Rota /download envia o arquivo];
    T --> U[End: Download Concluído];

    %% Estilos para clareza
    style G fill:#2a9d8f,stroke:#333,stroke-width:2px,color:white
    style M fill:#e76f51,stroke:#333,stroke-width:2px,color:white
    style U fill:#264653,stroke:#333,stroke-width:2px,color:white
    style B fill:#e9c46a,stroke:#333
    style R fill:#e9c46a,stroke:#333
    
---

### 📋 Tabela de Conteúdos
1.  [Sobre o Projeto](#-sobre-o-projeto)
2.  [🚀 Funcionalidades Principais](#-funcionalidades-principais)
3.  [🔧 Arquitetura Técnica](#-arquitetura-técnica)
4.  [🧠 Mapa Mental do Pipeline de IA](#-mapa-mental-do-pipeline-de-ia)
5.  [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
6.  [⚙️ Instalação e Execução](#️-instalação-e-execução)
7.  [📈 Melhorias Futuras](#-melhorias-futuras)
8.  [📄 Licença](#-licença)

---

## 📖 Sobre o Projeto

Este projeto foi criado para resolver um desafio comum no mundo corporativo: a necessidade de extrair, analisar e sintetizar rapidamente informações de documentos densos. Em vez de gastar horas lendo e estruturando manualmente, esta ferramenta automatiza todo o processo.

O usuário simplesmente faz o upload de um arquivo de origem, e o sistema ativa um "cérebro" de IA que:
1.  **Lê e compreende** o conteúdo.
2.  **Identifica** os temas mais relevantes.
3.  **Aprofunda a análise** em cada tema, identificando riscos e oportunidades.
4.  **Sintetiza** uma conclusão estratégica e um resumo executivo.
5.  **Monta** tudo em um relatório profissional e editável no formato `.docx`.

O resultado é uma economia massiva de tempo e um aumento na capacidade de tomada de decisão, fornecendo insights estruturados de forma quase instantânea.

## 🚀 Funcionalidades Principais

-   **Upload Multi-formato:** Aceita uma vasta gama de tipos de arquivo (`.pdf`, `.docx`, `.pptx`, `.jpg`, `.html`, etc.), normalizando todos para análise.
-   **Pipeline de IA Multi-Etapas:** Em vez de uma única chamada de IA, o sistema orquestra uma sequência de tarefas especializadas, garantindo maior profundidade e qualidade.
-   **Engenharia de Prompt Baseada em Personas:** Cada etapa do pipeline atribui uma "persona" específica à IA (ex: *Analista Sênior*, *CSO*, *Editor-Chefe*) para otimizar a qualidade da saída para cada tarefa.
-   **Feedback de Processamento em Tempo Real:** A interface web exibe o status atual do processamento, informando ao usuário exatamente em qual etapa seu documento se encontra.
-   **Saída Editável:** O relatório final é entregue em formato `.docx`, permitindo que o usuário faça ajustes e personalizações facilmente.

## 🔧 Arquitetura Técnica

O projeto é dividido em três camadas principais:

1.  **Frontend (Interface do Usuário):**
    -   Construído com **Flask** servindo um template **Jinja2** (`index.html`).
    -   Estilizado com **Bootstrap 5** para um design moderno e responsivo.
    -   Utiliza **JavaScript** nativo para realizar chamadas assíncronas (polling) ao endpoint `/status` a cada 2 segundos, atualizando dinamicamente o overlay de carregamento com o progresso do backend.

2.  **Backend (Servidor Flask):**
    -   Gerencia as rotas da aplicação: `/` para o upload, `/status` para o feedback de progresso e `/download` para a entrega do arquivo final.
    -   Lida com o upload seguro de arquivos e os armazena temporariamente na pasta `uploads/`.
    -   Orquestra a chamada para a função principal `processar_e_gerar_pdf`, que contém a lógica de negócios e o pipeline de IA.
    -   Utiliza o sistema de `logging` do Python para registrar cada etapa em `app.log`, que é lido pelo endpoint `/status`.

3.  **Pipeline de IA (O "Cérebro"):**
    -   O coração da aplicação, executado dentro da função `processar_e_gerar_pdf`.
    -   É uma sequência de funções que invocam modelos de linguagem (GPT/Gemini) com prompts altamente especializados e detalhados.
    -   Cada etapa gera uma parte do relatório (tópicos, análises, conclusão), que é passada como entrada para a etapa seguinte, criando uma cadeia de valor de informação.
    -   Ao final, todos os componentes textuais são montados em um único documento Markdown, que é então convertido para `.docx` usando a biblioteca `python-docx`.

## 🧠 Mapa Mental do Pipeline de IA

Este mapa descreve o fluxo de dados e transformações desde o upload até o relatório final.

-   **🚀 INÍCIO: AÇÃO DO USUÁRIO**
    -   `[Formulário Web]` Preenche Autor, Status e faz upload de um arquivo (`.pdf`, `.docx`, etc.).
    -   `[Requisição POST para /]` O arquivo é enviado ao servidor Flask.

-   **ETAPA 1: NORMALIZAÇÃO DO INPUT**
    -   `Input:` Arquivo original (qualquer formato).
    -   `Módulo:` `transformar_arq_txt.gerar_markdown()`
    -   `Tarefa:` Converter o arquivo para um texto limpo em formato Markdown.
    -   `Output:` String de texto em Markdown.

-   **ETAPA 2: IDENTIFICAÇÃO DE TÓPICOS**
    -   `Input:` Texto em Markdown.
    -   `Persona IA:` *Analista de Estratégia Sênior*.
    -   `Prompt:` `prompt_analisador_topicos`.
    -   `Tarefa:` Identificar os temas centrais e sua hierarquia.
    -   `Output:` Um objeto JSON com a estrutura de tópicos (ex: `{"Tópico 1": ..., "Tópico 1.1": ...}`).

-   **ETAPA 3: ANÁLISE APROFUNDADA (DEEP DIVE)**
    -   `Input:` Texto em Markdown + um tópico específico do JSON da etapa anterior.
    -   `Persona IA:` *Principal Strategy Consultant*.
    -   `Prompt:` `prompt_gerador_texto_topicos`.
    -   `Tarefa:` Escrever um mini-relatório detalhado para **cada tópico**, com riscos, oportunidades e recomendações.
    -   `Output:` Um dicionário de relatórios (`{"Relatório Tópico 1": "...", "Relatório Tópico 2": "..."}`).

-   **ETAPA 4 & 5 & 6: SÍNTESE ESTRATÉGICA**
    -   `Input:` Dicionário de relatórios + texto original.
    -   `Processos Paralelos:`
        -   **Conclusão:** `Persona IA: Chief Strategy Officer` -> `prompt_gerador_conclusao`.
        -   **Resumo:** `Persona IA: Analista de Comunicação Executiva` -> `prompt_gerador_resumo`.
        -   **Título:** `Persona IA: Editor-Chefe` -> `prompt_gerador_titulo`.
    -   `Output:` Componentes textuais separados (Conclusão, Resumo, Título, Subtítulo).

-   **ETAPA 7: MONTAGEM DO RELATÓRIO MESTRE**
    -   `Input:` Todos os componentes gerados (Título, Resumo, Relatórios, Conclusão, Autor, Data).
    -   `Persona IA:` *Arquiteto de Relatórios*.
    -   `Prompt:` `prompt_gerador_relatorio`.
    -   `Tarefa:` Montar todas as peças em um único documento Markdown, com índice e formatação hierárquica correta.
    -   `Output:` Uma string única contendo o relatório completo em Markdown.

-   **ETAPA 8: GERAÇÃO DO ARQUIVO FINAL**
    -   `Input:` String completa do relatório em Markdown.
    -   `Módulo:` `pdf_to_wrod.converter_string_markdown_para_word()`.
    -   `Tarefa:` Converter a string Markdown para um documento Microsoft Word.
    -   `Output:` Arquivo `.docx` salvo na pasta `processed_files/`.

-   **🏁 FIM: ENTREGA AO USUÁRIO**
    -   `[Renderização da Página]` A página é recarregada.
    -   `[Link de Download]` Um link para o arquivo `.docx` gerado aparece na interface.

## 🛠️ Tecnologias Utilizadas

-   **Backend:** Python, Flask
-   **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
-   **Inteligência Artificial:** Modelos de Linguagem (via API, ex: OpenAI, Google Gemini)
-   **Manipulação de Documentos:** `python-docx`, `pypdf`, `python-pptx` (dentro do seu módulo `transformar_arq_txt`)

## ⚙️ Instalação e Execução

Siga os passos abaixo para executar o projeto localmente.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    -   Crie um arquivo chamado `.env` na raiz do projeto.
    -   Adicione suas chaves e configurações. Use o arquivo `.env.example` como modelo:
    ```ini
    # .env.example
    FLASK_APP=app.py
    FLASK_DEBUG=True
    SECRET_KEY="sua-chave-secreta-forte-aqui"
    OPENAI_API_KEY="sk-..." 
    # ou a chave da API que você estiver usando
    ```

5.  **Crie as pastas necessárias:**
    ```bash
    mkdir uploads
    mkdir processed_files
    ```

6.  **Execute a aplicação:**
    ```bash
    flask run
    ```
    Acesse `http://127.0.0.1:5000` no seu navegador.

## 📈 Melhorias Futuras

-   [ ] **Processamento Assíncrono:** Implementar **Celery** e **Redis** para mover o pipeline de IA para uma fila de tarefas. Isso evitará timeouts e tornará a aplicação mais escalável e responsiva.
-   [ ] **Geração de PDF Aprimorada:** Reativar a geração de PDF, mas utilizando templates Jinja2 + WeasyPrint no backend para garantir um layout consistente e profissional, em vez de depender da IA para gerar HTML/CSS.
-   [ ] **Cache de Resultados:** Implementar um sistema de cache para evitar o reprocessamento de arquivos idênticos.
-   [ ] **Containerização com Docker:** Criar um `Dockerfile` e `docker-compose.yml` para facilitar o deploy e garantir a consistência do ambiente.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
