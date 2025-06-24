# Projeto de Anonimização de Dados com k-Anonimato e l-Diversidade

## Descrição do Projeto

Este projeto implementa técnicas de preservação de privacidade de dados, especificamente aplicando os conceitos de k-anonimato e l-diversidade em um dataset de **COVID-19 do Ceará**. O objetivo é proteger a identidade dos indivíduos enquanto mantém a utilidade dos dados para análises estatísticas.

A linguagem utilizada para a construção do projeto foi **Python**, com as bibliotecas **Pandas** para manipulação de dados e **Matplotlib** para visualização, além da classe **Counter** para facilitar a contagem dos elementos sensíveis do dataset e distinguir quantas classes satisfazem ou não a l-diversidade de forma mais rápida e otimizada.

## Estrutura do Código

- **Funções de Carregamento e Preparação**: Carregam os dados de entrada e realizam a supressão de identificadores explícitos como 'nome' e 'cpf'.
- **Funções de Generalização Hierárquica**: Aplicam generalização em atributos quasi-identificadores como 'localidade' e 'data_nascimento' em diferentes níveis para alcançar o k-anonimato.
- **Funções de Contagem e Análise**: Calculam o tamanho médio das classes de equivalência e a contagem de valores distintos para atributos sensíveis.
- **Função Principal de k-Anonimato**: Garante que cada registro no conjunto de dados anonimizado seja indistinguível de pelo menos `k-1` outros registros com base nos atributos quasi-identificadores.
- **Função Avançada: k-Anonimato + l-Diversidade**: Assegura que cada classe de equivalência contenha pelo menos `l` valores distintos para um atributo sensível (neste caso, 'raca_cor').
- **Funções de Avaliação**: Avaliam a perda de informação introduzida pela generalização e calculam a precisão formal.
- **Funções de Visualização**: Geram histogramas para visualizar o tamanho das classes de equivalência e a distribuição da l-diversidade.

## Funcionalidades

- **Carregamento de Dados**: Carrega dados de um arquivo CSV (`dados_covid-ce_02.csv`).
- **Supressão de Identificadores Explícitos**: Remove colunas como 'nome' e 'cpf' para garantir a privacidade.
- **Generalização Hierárquica**: Aplica generalização em atributos como 'localidade' e 'data_nascimento' em diferentes níveis para alcançar o k-anonimato.
- **k-Anonimato**: Garante que cada registro no conjunto de dados anonimizado seja indistinguível de pelo menos `k-1` outros registros com base nos atributos quasi-identificadores.
- **l-Diversidade**: Assegura que cada classe de equivalência (grupo de registros indistinguíveis) contenha pelo menos `l` valores distintos para um atributo sensível (neste caso, 'raca_cor').
- **Cálculo de Precisão Formal**: Avalia a perda de informação introduzida pela generalização.
- **Análise de Classes de Equivalência**: Calcula o tamanho médio das classes e a contagem de valores distintos para o atributo sensível.
- **Visualização de Dados**: Gera histogramas para visualizar o tamanho das classes de equivalência e a distribuição da l-diversidade.
- **Exportação de Dados Anonimizados**: Salva os dados anonimizados em arquivos CSV.

## Como Usar

1.  **Pré-requisitos**:

    - Python 3.x
    - Bibliotecas Python: `pandas`, `matplotlib`

    Você pode instalar as bibliotecas necessárias usando pip:

    ```bash
    pip install pandas matplotlib
    ```

2.  **Dados de Entrada**:
    Certifique-se de ter um arquivo CSV chamado `dados_covid-ce_02.csv` no mesmo diretório do script. Este arquivo deve conter as colunas 'nome', 'cpf', 'localidade', 'data_nascimento' e 'raca_cor'.

3.  **Execução**:
    Execute o script Python:

    ```bash
    python main.py
    ```

    O script irá processar os dados para diferentes valores de `k` (2, 4, 8) e `l` (variando de acordo com `k`), gerar histogramas e salvar os dados anonimizados em arquivos CSV como `dados_generalizados_k=<k>_l=<l>.csv`.

## Participantes

- João Gabriel Nogueira da Silva
- Kayo de Almeida Pereira
- Keven Lucas Almeida de Oliveira
