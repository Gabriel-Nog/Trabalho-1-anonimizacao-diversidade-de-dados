import pandas as pd
from collections import Counter
import os

def carregar_dados():
    file = pd.read_csv('dados_covid-ce_reduzido.csv', sep=';')
    return file.copy()

def suprimir_identificadores(df):
    df['nome'] = '*'
    df['cpf'] = '*'
    return df

def generalizar_localidade(valor, nivel):
    if nivel == 0:
        return valor  # bairro/cidade/estado
    elif nivel == 1:
        return valor.split('/')[1] + '/CE' if '/' in valor else 'CE'
    elif nivel == 2:
        return 'CE'
    return valor

def generalizar_data_nascimento(valor, nivel):
    try:
        partes = valor.split('/')
        if nivel == 0:
            return valor  # dd/mm/aaaa
        elif nivel == 1:
            return f'{partes[1]}/{partes[2]}'
        elif nivel == 2:
            return partes[2]
    except:
        return '*'
    return valor

def generalizar_raca_cor(valor):
    return 'Sem informação' if valor not in ['PARDA', 'BRANCA', 'PRETA', 'AMARELA', 'INDÍGENA'] else valor

def aplicar_generalizacoes(df, nivel_localidade, nivel_data):
    df['localidade'] = df['localidade'].apply(lambda x: generalizar_localidade(x, nivel_localidade))
    df['data_nascimento'] = df['data_nascimento'].apply(lambda x: generalizar_data_nascimento(x, nivel_data))
    df['raca_cor'] = df['raca_cor'].apply(lambda x: generalizar_raca_cor(x))
    return df

def aplicar_k_anonimato(df, k, qids):
    grupo = df.groupby(qids)
    contagem = grupo.size().reset_index(name='count')

    df_completo = df.merge(contagem, on=qids)
    df_filtrado = df_completo[df_completo['count'] >= k].drop(columns=['count'])
    return df_filtrado

def calcular_precisao(df, qids, profundidades):
    N = len(df)
    M = len(qids)
    perda_total = 0.0

    for i in range(N):
        for atributo in qids:
            valor = df.iloc[i][atributo]
            nivel = calcular_nivel(valor, atributo)
            perda_total += nivel / profundidades[atributo]

    perda = perda_total / (N * M)
    return 1 - perda

def calcular_nivel(valor, atributo):
    if atributo == 'localidade':
        if valor == 'CE':
            return 2
        elif valor.endswith('/CE'):
            return 1
        else:
            return 0
    elif atributo == 'data_nascimento':
        if valor.count('/') == 0 and len(valor) == 4:
            return 2
        elif valor.count('/') == 1:
            return 1
        else:
            return 0
    elif atributo == 'raca_cor':
        return 1 if valor == 'Sem informação' else 0
    return 0

def salvar_dataset(df, k, l):
    nome_arquivo = f'dados_covid-ce_{k}_{l}.csv'
    df.to_csv(nome_arquivo, sep=';', index=False)
    print(f"✅ Dataset salvo como: {nome_arquivo}")

def processar_k_anonimato(k, l):
    df = carregar_dados()
    df = suprimir_identificadores(df)

    # Hierarquia mais alta para atingir k-anonimato mais fácil
    nivel_localidade = 2 if k >= 8 else 1 if k >= 4 else 1
    nivel_data = 2 if k >= 8 else 1 if k >= 4 else 2

    df = aplicar_generalizacoes(df, nivel_localidade, nivel_data)

    qids = ['localidade', 'data_nascimento', 'raca_cor']
    df_anon = aplicar_k_anonimato(df, k, qids)

    if df_anon.empty:
        print(f"❌ Nenhum dado resultante após aplicar k={k}")
        return

    salvar_dataset(df_anon, k, l)

    profundidades = {'localidade': 3, 'data_nascimento': 3, 'raca_cor': 2}
    precisao = calcular_precisao(df_anon, qids, profundidades)
    print(f"🎯 Precisão para k={k}, l={l}: {precisao:.4f}")

    tamanho_medio = len(df_anon) / df_anon.groupby(qids).ngroups
    print(f"📊 Tamanho médio das classes de equivalência: {tamanho_medio:.2f}")

# Exemplos de execução
k_list = [2, 4, 8]
l_dict = {
    2: [2],
    4: [2, 3, 4],
    8: [2, 3, 4]
}

for k in k_list:
    for l in l_dict[k]:
        print(f"\n🔧 Processando para k={k}, l={l}")
        processar_k_anonimato(k, l)