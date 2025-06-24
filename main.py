import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Função para carregar os dados originais
def carregar_dados():
    df = pd.read_csv('dados_covid-ce_02.csv', sep=';')
    return df

# Função para suprimir identificadores explícitos
def suprimir_dados(df):
    df['nome'] = '*'
    df['cpf'] = '*'
    return df

# Função de hierarquia de generalização para localidade
def hierarquia_localidade(valor, nivel):
    try:
        partes = valor.split('/')
        partes += [''] * (3 - len(partes))  # Ex: [bairro, cidade, estado]
        if nivel == 0:
            return f"{partes[0]}/{partes[1]}/{partes[2]}"
        elif nivel == 1:
            return f"{partes[1]}/{partes[2]}" if partes[1] and partes[2] else partes[2] or '*'
        elif nivel == 2:
            return partes[2] if partes[2] else '*'
        else:
            return '*'
    except:
        return '*'

# Função de hierarquia de generalização para data de nascimento
def hierarquia_data_nascimento(valor, nivel):
    try:
        partes = valor.split('/')
        # partes = [dd, mm, YYYY]
        if len(partes) != 3:
            return '*'
        dia, mes, ano = partes
        if nivel == 0:
            return valor  # dd/mm/YYYY
        elif nivel == 1:
            return f"{mes}/{ano}"  # mm/YYYY
        elif nivel == 2:
            return ano  # YYYY
        else:
            return '*'
    except:
        return '*'

# Função para contar ocorrências por classe de equivalência (localidade + data_nascimento)
def contar_ocorrencias_localidade_data(df):
    if 'contagem' in df.columns:
        df = df.drop('contagem', axis=1)
    contagem = df.groupby(['localidade', 'data_nascimento']).size().reset_index(name='contagem')
    df = df.merge(contagem, on=['localidade', 'data_nascimento'], how='left')
    return df

# Aplica generalização incremental até que todas as classes satisfaçam o k-anonimato
def generalizar_ate_k_anonimato(df, k, nivel_maximo=4):
    df['localidade'] = df['localidade'].fillna('').astype(str)
    df['data_nascimento'] = df['data_nascimento'].fillna('').astype(str)
    nivel = 0
    while nivel <= nivel_maximo:
        df = contar_ocorrencias_localidade_data(df)
        mask = df['contagem'] < k
        if not mask.any():
            break
        df.loc[mask, 'localidade'] = df.loc[mask, 'localidade'].apply(lambda x: hierarquia_localidade(x, nivel))
        df.loc[mask, 'data_nascimento'] = df.loc[mask, 'data_nascimento'].apply(lambda x: hierarquia_data_nascimento(x, nivel))
        nivel += 1
    df = contar_ocorrencias_localidade_data(df)
    return df

# Calcula a precisão formal baseada na fórmula do trabalho (1 - perda de informação)
def calcular_precisao(df_original, df_generalizado):
    profundidade_hierarquia = 3
    total_registros = len(df_original)
    if total_registros == 0:
        return 0.0

    def nivel_localidade(valor):
        if valor == '*': return 3
        if '/' not in valor: return 2
        partes = valor.split('/')
        if len(partes) == 3: return 0
        if len(partes) == 2: return 1
        return 2

    def nivel_data(valor):
        if valor == '*': return 3
        if '/' not in valor: return 2
        partes = valor.split('/')
        if len(partes) == 3: return 0  # dd/mm/yyyy
        if len(partes) == 2: return 1  # mm/yyyy
        return 2

    soma_niveis = 0
    for loc, data in zip(df_generalizado['localidade'], df_generalizado['data_nascimento']):
        soma_niveis += nivel_localidade(loc) + nivel_data(data)

    perda_info = soma_niveis / (total_registros * 2 * profundidade_hierarquia)
    precisao = (1 - perda_info) * 100
    return precisao

    # Aplica k-anonimato + l-diversidade com generalização conjunta
def aplicar_l_diversidade_com_generalizacao(df, k, l, nivel_maximo=4):
    df['localidade'] = df['localidade'].fillna('').astype(str)
    df['data_nascimento'] = df['data_nascimento'].fillna('').astype(str)
    if 'raca_cor' in df.columns:
        df['raca_cor'] = df['raca_cor'].fillna('Não informado')
    nivel = 0
    while nivel <= nivel_maximo:
        df_temp = df.copy()
        df_temp = contar_ocorrencias_localidade_data(df_temp)
        contagem_racas = df_temp.groupby(['localidade', 'data_nascimento'])['raca_cor'].nunique().reset_index(name='contagem_raca_cor')
        df_temp = df_temp.merge(contagem_racas, on=['localidade', 'data_nascimento'], how='left')
        mask_k = df_temp['contagem'] < k
        mask_l = df_temp['contagem_raca_cor'] < l
        if not mask_k.any() and not mask_l.any():
            print(f"✅ k={k} e l={l} satisfeitos no nível {nivel}")

            classes_info = []
            grouped = df_temp.groupby(['localidade', 'data_nascimento'])
            for (localidade, data), grupo in grouped:
                valores_distintos = grupo['raca_cor'].nunique()
                classes_info.append({
                    'localidade': localidade,
                    'data_nascimento': data,
                    'tamanho': len(grupo),
                    'valores_distintos': valores_distintos,
                    'satisfaz_l': valores_distintos >= l
                })
            return df_temp, classes_info
        mask_generalizacao = mask_k | mask_l
        if mask_generalizacao.any():
            print(f"⚠️  Generalizando no nível {nivel}: k-anonimato={'não satisfeito' if mask_k.any() else 'satisfeito'}, l-diversidade={'não satisfeita' if mask_l.any() else 'satisfeita'}")
            df.loc[mask_generalizacao, 'localidade'] = df.loc[mask_generalizacao, 'localidade'].apply(lambda x: hierarquia_localidade(x, nivel))
            df.loc[mask_generalizacao, 'data_nascimento'] = df.loc[mask_generalizacao, 'data_nascimento'].apply(lambda x: hierarquia_data_nascimento(x, nivel))
        nivel += 1
    df_final = contar_ocorrencias_localidade_data(df)
    contagem_racas = df_final.groupby(['localidade', 'data_nascimento'])['raca_cor'].nunique().reset_index(name='contagem_raca_cor')
    df_final = df_final.merge(contagem_racas, on=['localidade', 'data_nascimento'], how='left')
    print(f"❌ Não foi possível satisfazer k={k} e l={l} simultaneamente no nível máximo {nivel_maximo}")
    return df_final, []

# Calcula o tamanho médio das classes de equivalência
def calcular_tamanho_medio_classes(df):
    total_registros = len(df)
    classes_equivalencia = df.groupby(['localidade', 'data_nascimento']).size()
    num_classes = len(classes_equivalencia)
    if num_classes == 0:
        return 0
    return total_registros / num_classes


def gerar_histograma_top_classes(df, k):
    classes_equivalencia = df.groupby(['localidade', 'data_nascimento']).size().reset_index(name='tamanho')
    top_classes = classes_equivalencia.nlargest(15, 'tamanho')
    labels = [f"{row['localidade']}\n{row['data_nascimento']}" for _, row in top_classes.iterrows()]
    plt.figure(figsize=(15, 8))
    bars = plt.bar(range(len(top_classes)), top_classes['tamanho'], color='lightblue', edgecolor='navy', alpha=0.7)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=9)
    plt.xlabel('Classes de Equivalência')
    plt.ylabel('Tamanho da Classe')
    plt.title(f'Top 15 Maiores Classes - k={k}')
    plt.xticks(range(len(top_classes)), labels, rotation=45, ha='right', fontsize=8)
    plt.axhline(y=k, color='red', linestyle='--', label=f'k = {k}')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()
    print("📊 Histograma das classes concluído.")

def gerar_histograma_l_diversidade(classes_info, l, k):
    valores_distintos = [c['valores_distintos'] for c in classes_info]
    plt.figure(figsize=(10, 6))
    max_valores = max(valores_distintos) if valores_distintos else 1
    bins = range(1, max_valores + 2)
    plt.hist(valores_distintos, bins=bins, align='left', rwidth=0.8, color='skyblue', edgecolor='black')
    plt.axvline(x=l, color='red', linestyle='--', linewidth=2, label=f'l = {l} (mínimo)')
    plt.xlabel('Nº de valores distintos do atributo sensível (raça/cor)')
    plt.ylabel('Frequência de classes')
    plt.title(f'Histograma de l-diversidade\nk={k}, l={l}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    print("📊 Histograma da l-diversidade concluído.")


# Execução principal
k_list = [2, 4, 8]
l_dict = {
    2: [2],
    4: [2, 3],
    8: [2, 3, 4]
}

df_original = carregar_dados()
print(f"Dataset original: {len(df_original)} registros\n")

df_original = suprimir_dados(df_original)

for k in k_list:
    print("=" * 60)
    print(f"🛡️  k-anonimato: k = {k}")
    df_k = generalizar_ate_k_anonimato(df_original.copy(), k)

    precisao = calcular_precisao(df_original, df_k)
    print(f" - Precisão após k-anonimato: {precisao:.2f}%")

    for l in l_dict[k]:
        print("-" * 40)
        print(f"🔐 l-diversidade: l = {l}")

        df_final, classes_info = aplicar_l_diversidade_com_generalizacao(df_k.copy(), k, l)

        sat_k = (df_final['contagem'] >= k).all()
        sat_l = (df_final['contagem_raca_cor'] >= l).all()

        print(f" - k-anonimato (k≥{k}): {'✅ Satisfeito' if sat_k else '❌ Não satisfeito'}")
        print(f" - l-diversidade (l≥{l}): {'✅ Satisfeito' if sat_l else '❌ Não satisfeito'}")

        print(f"\n📈 Estatísticas das classes de equivalência:")
        valores_distintos = [classe['valores_distintos'] for classe in classes_info]
        contagem_classes = Counter(valores_distintos)
        for valor, qtd in sorted(contagem_classes.items()):
            print(f"   - Classes com {valor} valor(es) distinto(s): {qtd}")

        print(f" - Tamanho médio das classes: {calcular_tamanho_medio_classes(df_final):.2f}")

        print("\n📊 Gerando histogramas...")
        gerar_histograma_top_classes(df_final, k)
        gerar_histograma_l_diversidade(classes_info, l, k)

        nome_arquivo = f"dados_generalizados_k={k}_l={l}.csv"
        df_final.to_csv(nome_arquivo, sep=';', index=False)
        print(f"💾 Arquivo salvo: {nome_arquivo}\n")