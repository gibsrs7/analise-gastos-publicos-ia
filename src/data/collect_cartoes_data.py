import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a chave da API do ambiente
API_KEY = os.getenv("PORTAL_API_KEY")

if not API_KEY:
    print("Erro: Chave da API não encontrada. Verifique seu arquivo .env e a variável PORTAL_API_KEY.")
    exit()

# Definir o cabeçalho da requisição com a chave da API
headers = {
    "chave-api-dados": API_KEY
}

# Parâmetros da API utilizando os filtros corretos da documentação
# Formato para mesExtratoInicio e mesExtratoFim é "MM/AAAA"
# Vamos pegar dados de Janeiro de 2024 como exemplo.
MES_INICIO = "01/2024"  # Altere para o mês/ano de início que você queira consultar
MES_FIM = "01/2024"    # Altere para o mês/ano de fim que você queira consultar
PAGINA_CONSULTA = 1

params = {
    "mesExtratoInicio": MES_INICIO,
    "mesExtratoFim": MES_FIM,
    "pagina": PAGINA_CONSULTA
    # Você pode adicionar outros filtros opcionais aqui conforme a documentação,
    # por exemplo: "codigoOrgao": "CODIGO_DO_ORGAO_SIAFI"
}

# URL base da API para gastos com cartão
base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/cartoes"

print(f"Buscando dados de gastos com cartão de {MES_INICIO} a {MES_FIM}, página {PAGINA_CONSULTA}...")

try:
    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()  # Lança uma exceção para respostas de erro (4xx ou 5xx)

    data = response.json()  # Converte a resposta JSON em uma lista de dicionários Python

    if data:
        # Converter os dados para um DataFrame do Pandas
        df = pd.DataFrame(data)

        print("\n### Informações do DataFrame ###")
        df.info()

        print("\n### Primeiras 5 Linhas do DataFrame ###")
        print(df.head())

        print(f"\n### Dimensões do DataFrame (linhas, colunas) para a página {PAGINA_CONSULTA} ###")
        print(df.shape)

        # Onde salvar os dados (dentro de uma nova pasta 'data/raw')
        output_dir = "src/data/raw"
        os.makedirs(output_dir, exist_ok=True) # Cria o diretório se não existir

        # Nome do arquivo (ajustado para refletir o período)
        file_name = f"gastos_cartao_{MES_INICIO.replace('/', '-')}_a_{MES_FIM.replace('/', '-')}_pagina_{PAGINA_CONSULTA}.csv"
        output_path = os.path.join(output_dir, file_name)

        # Salvar o DataFrame em um arquivo CSV
        df.to_csv(output_path, index=False)
        print(f"\nDados salvos em: {output_path}")

    else:
        print("Nenhum dado encontrado para os parâmetros fornecidos. Verifique os parâmetros e se há dados para o período.")
        if response.status_code == 200 and not data: # Requisição OK, mas sem conteúdo
             print("A API retornou uma lista vazia, o que pode ser normal se não houver dados para o filtro especificado.")

except requests.exceptions.HTTPError as http_err:
    print(f"Erro HTTP: {http_err}")
    print(f"Status Code: {response.status_code}")
    print(f"Conteúdo da resposta: {response.text}")
except requests.exceptions.RequestException as req_err:
    print(f"Erro na requisição: {req_err}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")