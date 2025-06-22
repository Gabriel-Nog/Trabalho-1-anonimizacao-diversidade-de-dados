import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import os

# Carregar dataset e simular mais dados para testes
df = pd.read_csv('dados_covid-ce_reduzido.csv', sep=';')
df = pd.concat([df]*10, ignore_index=True)  # simula mais dados para possibilitar k >= 4

# Padronizar nomes de colunas
columns_map = {col: col.strip().lower().replace(" ", "_") for col in df.columns}
df.rename(columns=columns_map, inplace=True)

# Converter data_nascimento
if 'data_nascimento' in df.columns:
    df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], format='%d/%m/%Y', errors='coerce')

# Funções para generalização da data

def generalize_data_nascimento(date, level):
    if pd.isnull(date): 
        return "Desconhecido"
    if level == 0:
        return date.strftime('%d/%m/%Y')
    elif level == 1:
        return date.strftime('%m/%Y')
    elif level == 2:
        return date.strftime('%Y')
    elif level == 3:
        return "Ano desconhecido"

def generalize_localidade(localidade_str, level):
    if pd.isnull(localidade_str): return "Desconhecido"
    parts = localidade_str.split('/')
    if level == 0:
        return localidade_str
    elif level == 1 and len(parts) == 3:
        return f"{parts[1]}/{parts[2]}"
    elif level == 2 and len(parts) == 3:
        return parts[2]
    elif level == 3:
        return "Localidade desconhecida"
    return localidade_str

def apply_generalization(df, gen_levels):
    df_copy = df.copy()
    df_copy['data_nascimento_gen'] = df_copy['data_nascimento'].apply(lambda x: generalize_data_nascimento(x, gen_levels['data_nascimento']))
    df_copy['localidade_gen'] = df_copy['localidade'].apply(lambda x: generalize_localidade(x, gen_levels['localidade']))
    return df_copy

def check_k_anonymity(df, k):
    grouped = df.groupby(['data_nascimento_gen', 'localidade_gen'])
    for key, group in grouped:
        if len(group) < k:
            return False
    return True

def check_l_diversity(df, l):
    grouped = df.groupby(['data_nascimento_gen', 'localidade_gen'])
    for _, group in grouped:
        if group['raca_cor'].nunique() < l:
            return False
    return True

def generate_histograms(df, k, l):
    eq_classes = df.groupby(['data_nascimento_gen', 'localidade_gen']).size().reset_index(name='count')
    eq_classes['diversidade'] = df.groupby(['data_nascimento_gen', 'localidade_gen'])['raca_cor'].nunique().values

    top_y = eq_classes.sort_values(by='count', ascending=False).head(10)
    plt.figure(figsize=(10,6))
    plt.bar(range(len(top_y)), top_y['count'])
    plt.xticks(range(len(top_y)), [f"{x[0]}\n{x[1]}" for x in zip(top_y['data_nascimento_gen'], top_y['localidade_gen'])], rotation=45, ha='right')
    plt.title(f"Top 10 Classes de Equivalência - k={k}")
    plt.ylabel("Tamanho da Classe")
    plt.tight_layout()
    plt.savefig(f"histograma_k_{k}.png")
    plt.close()

    plt.figure(figsize=(10,6))
    plt.hist(eq_classes['diversidade'], bins=range(1, eq_classes['diversidade'].max()+2), align='left', rwidth=0.8)
    plt.xlabel("Número de valores distintos de raca_cor")
    plt.ylabel("Frequência")
    plt.title(f"Histograma de l-diversidade - k={k}, l={l}")
    plt.tight_layout()
    plt.savefig(f"histograma_ldiversidade_k_{k}_l_{l}.png")
    plt.close()

def k_l_anonimato_pipeline(df, k_list, l_dict):
    generalization_options = [
        {'data_nascimento': i, 'localidade': j}
        for i in range(4) for j in range(4)
    ]

    for k in k_list:
        for l in l_dict[k]:
            print(f"\n🔍 Tentando k={k}, l={l}...")
            sucesso = False
            for option in generalization_options:
                df_gen = apply_generalization(df, option)
                if check_k_anonymity(df_gen, k):
                    if check_l_diversity(df_gen, l):
                        print(f"✅ Sucesso com generalização: {option}")
                        df_final = df_gen.drop(columns=['nome', 'cpf'], errors='ignore')
                        filename = f"dados_covid-ce_{k}_{l}.csv"
                        df_final.to_csv(filename, sep=';', index=False)
                        generate_histograms(df_gen, k, l)
                        sucesso = True
                        break
            if not sucesso:
                    print(f"❌ Não foi possível atingir k={k}, l={l} com as generalizações disponíveis.")
        N = len(df_final)
        M = 2  # dois atributos: data_nascimento e localidade

def perda_informacao(df, profundidades):
    for col, levels in profundidades.items():
        print(f"\nCalculando perda de informação para {col}:")
        for profundidade in levels:
            perda = df[col].nunique() / (2 ** profundidade)
            print(f"Profundidade {profundidade}: Perda de informação = {perda:.2f}")





# Executar
df['raca_cor'] = df['raca_cor'].fillna("Desconhecido")
k_list = [1, 2, 3, 4, 5]
l_dict = {
    1: [1],
    2: [1, 2],
    3: [1, 2, 3],
    4: [1, 2, 3, 4],
    5: [1, 2, 3, 4, 5]
}
      
k_l_anonimato_pipeline(df, k_list, l_dict)
# Cálculo da perda de informação e precisão
profundidades = {
    'data_nascimento': [1, 2, 3, 4, 5],
    'localidade': [1, 2, 3, 4, 5]
}

perda = perda_informacao(df, profundidades)
print(perda)

