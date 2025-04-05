import pandas as pd

# Caminho do arquivo
arquivo_excel = 'Datasets/ESFT0100.csv'


colunas_fat = [
    'Cod Estab', 'Razao Social', 'Cidade', 'Estado', 'Canal Venda Cliente',
    'Dt Implant Ped', 'Ped Cliente', 'Ped Datasul', 'Tipo Oper',
    'Serie', 'Nota Fiscal', 'Natureza', 'Dt Emis NF', 'Dt Embarque',
    'Dt Aprov. Credito', 'Receita', 'Item', 'Desc Item', 'Deposito',
    'Quantidade', 'Vl Net Livro', 'Nro Embarque', 'Marca', 'Dt Entrega', 'Situacao Ped'
]


df_fat = pd.read_csv(arquivo_excel, usecols=colunas_fat, sep=';', encoding='ISO-8859-1')

# Padronizar nomes das colunas
df_fat.columns = (df_fat.columns.str.lower()
                      .str.replace(' ', '_')
                      .str.replace('.', '', regex=False))


# Converter colunas de data
colunas_datas = ['dt_implant_ped', 'dt_embarque', 'dt_aprov_credito']
for col in colunas_datas:
    if col in df_fat.columns and not pd.api.types.is_datetime64_any_dtype(df_fat[col]):
        df_fat[col] = pd.to_datetime(df_fat[col], errors='coerce', dayfirst=True)

# Preencher valores ausentes
df_fat.fillna({
    'canal_venda_cliente': 'Desconhecido',
    'ped_cliente': 'Sem Pedido',
    'deposito': 'Não Informado',
    'nro_embarque': 'Sem Embarque'
}, inplace=True)

# Converter coluna 'receita' para booleano
if 'receita' in df_fat.columns:
    df_fat['receita'] = df_fat['receita'].astype(str).str.strip().str.lower().map({'sim': True, 'não': False}).astype(bool)

# Converter colunas numéricas
colunas_numericas = ['vl_net_livro', 'quantidade']
for col in colunas_numericas:
    if col in df_fat.columns:
        df_fat[col] = (df_fat[col].astype(str)
                          .str.replace(',', '.', regex=False)
                          .str.replace('[^0-9.-]', '', regex=True)
                          .astype(float)
                          .abs())

# Remover marcas indesejadas
if 'marca' in df_fat.columns:
    marcas_indesejadas = {'?', 'METALIKA', 'MTK CD SP', 'PAPAIZ SOR'}
    df_fat = df_fat[~df_fat['marca'].isin(marcas_indesejadas)]

# Converter colunas para string
for col in ['ped_cliente', 'serie', 'natureza', 'item']:
    if col in df_fat.columns:
        df_fat[col] = df_fat[col].astype(str)

# Salvar em formato parquet
df_fat.to_parquet('Datasets/ESFT0100_historico.parquet', index=False)
print('Data Atualizada com sucesso!')