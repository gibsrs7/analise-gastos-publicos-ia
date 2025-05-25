import ollama
import pandas as pd
import os

MODEL_NAME = 'phi3:mini'
# Ajuste o caminho para o seu arquivo CSV, se necessário
# O script está em src/llm_interaction/, então o CSV está em ../data/raw/
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'gastos_cartao_01-2024_a_01-2024_pagina_1.csv')
# !!! IMPORTANTE: Confirme se 'gastos_cartao_01-2024_a_01-2024_pagina_1.csv' é o nome correto do seu arquivo !!!

def load_data(file_path):
    print(f"Carregando dados de: {file_path}")
    try:
        df = pd.read_csv(file_path)
        # Lembre-se da conversão de colunas que pareciam dicionários (strings)
        # Se você salvou o CSV após a conversão para dicts no notebook, pode não precisar disso.
        # Se o CSV tem as colunas como strings de dicts, precisaremos da função string_para_dict aqui.
        # Por simplicidade, vamos assumir que as colunas principais que usaremos (ex: valor, favorecido)
        # já estão em um formato razoável ou foram achatadas.
        # Para este exemplo, vamos focar em colunas que provavelmente são diretas no CSV.
        print(f"Dados carregados: {df.shape[0]} linhas, {df.shape[1]} colunas.")
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo CSV não encontrado em '{file_path}'. Verifique o caminho.")
        return None
    except Exception as e:
        print(f"Erro ao carregar o CSV: {e}")
        return None

def query_llm_with_context(prompt_text, context_data_string=""):
    full_prompt = f"""
    Você é um assistente prestativo que analisa dados financeiros.
    Analise os seguintes dados de transações e depois responda à pergunta.

    Dados Fornecidos:
    {context_data_string}

    Pergunta:
    {prompt_text}
    """
    # print(f"\n--- Prompt Completo Enviado para a LLM ---")
    # print(full_prompt) # Descomente para ver o prompt completo
    # print("---------------------------------------\n")

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': full_prompt.strip()}]
        )
        message_content = response['message']['content']
        print("\n--- Resposta da LLM ---")
        print(message_content)
        print("-----------------------\n")
        return message_content
    except Exception as e:
        print(f"Ocorreu um erro ao interagir com o Ollama: {e}")
        return None

if __name__ == '__main__':
    df = load_data(CSV_FILE_PATH)

    if df is not None and not df.empty:
        # Exemplo 1: Perguntar sobre as 3 transações de maior valor
        # Primeiro, preparamos o contexto com essas transações

        # Certifique-se que a coluna de valor é numérica
        # (Lembre-se da conversão que fizemos no notebook: str.replace('.', '').str.replace(',', '.').astype(float))
        # Vamos assumir que se chama 'valorTransacao' e precisa ser convertida.
        coluna_valor = 'valorTransacao' # CONFIRME O NOME DA COLUNA
        if coluna_valor in df.columns:
            if df[coluna_valor].dtype == 'object':
                try:
                    df[coluna_valor] = df[coluna_valor].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors='coerce')
                    print(f"Coluna '{coluna_valor}' convertida para numérico.")
                except Exception as e:
                    print(f"Falha ao converter '{coluna_valor}' para numérico: {e}. Os resultados podem ser inesperados.")

            if pd.api.types.is_numeric_dtype(df[coluna_valor]):
                top_3_transacoes = df.nlargest(3, coluna_valor)

                # Colunas que queremos mostrar para a LLM como contexto.
                # Se você já achatou 'favorecido' para 'favorecido_nome', use esse.
                # Por agora, vamos supor que 'favorecido' é uma string simples ou que você pegará a coluna achatada.
                # Se 'favorecido' for um dict stringificado, você precisaria aplicar string_para_dict e pegar o nome.
                colunas_de_contexto = [coluna_valor, 'favorecido.nome', 'orgaoSuperior.nome', 'dataTransacao'] # AJUSTE OS NOMES DAS COLUNAS!

                # Verifica se as colunas de contexto existem
                colunas_existentes_para_contexto = [col for col in colunas_de_contexto if col in top_3_transacoes.columns]

                if not colunas_existentes_para_contexto:
                    print("Erro: Nenhuma das colunas especificadas para contexto existem no DataFrame.")
                    print(f"Colunas disponíveis: {top_3_transacoes.columns.tolist()}")
                else:
                    contexto_top_3_str = top_3_transacoes[colunas_existentes_para_contexto].to_string(index=False)

                    pergunta1 = f"Com base nos dados das 3 transações de maior valor fornecidas, resuma brevemente quem foram os favorecidos e os órgãos superiores envolvidos."
                    query_llm_with_context(pergunta1, contexto_top_3_str)

                    pergunta2 = f"Qual foi o valor total dessas 3 transações listadas?"
                    query_llm_with_context(pergunta2, contexto_top_3_str)
            else:
                print(f"A coluna '{coluna_valor}' não é numérica. Não é possível encontrar as N maiores transações.")
        else:
            print(f"Coluna '{coluna_valor}' não encontrada no DataFrame.")

        # Exemplo 2: Pergunta geral (sem contexto de dados específicos, LLM pode alucinar ou recusar)
        # pergunta_geral = "Quais são os tipos de gastos mais comuns para o governo brasileiro com cartão de pagamento?"
        # print("\n--- Testando Pergunta Geral (sem contexto de dados específico) ---")
        # query_llm_with_context(pergunta_geral) # A LLM não terá acesso ao CSV aqui, apenas ao seu conhecimento geral.

    else:
        print("Não foi possível carregar os dados ou o DataFrame está vazio. Saindo.")