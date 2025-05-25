import ollama

MODEL_NAME = 'phi3:mini' # O modelo que você baixou e testou

def query_llm(prompt_text):
    print(f"Enviando prompt para o modelo '{MODEL_NAME}': '{prompt_text}'")
    try:
        # Usando ollama.chat (mais comum para modelos de chat como phi3)
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'user',
                    'content': prompt_text,
                }
            ]
        )
        print("\n--- Resposta da LLM ---")
        # A resposta completa é um dicionário, o conteúdo da mensagem está em response['message']['content']
        message_content = response['message']['content']
        print(message_content)
        print("-----------------------\n")
        return message_content

    except Exception as e:
        print(f"Ocorreu um erro ao interagir com o Ollama: {e}")
        print("Dicas:")
        print("1. Verifique se o Ollama está em execução.")
        print("   (Se você rodou 'ollama run phi3:mini' e fechou, o servidor pode ter parado).")
        print("   Você pode precisar iniciar o servidor Ollama em um terminal separado com: 'ollama serve'")
        print("   e mantê-lo rodando enquanto executa este script.")
        print("2. Verifique se o nome do modelo está correto.")
        return None

if __name__ == '__main__':
    # Teste 1: Pergunta simples
    prompt1 = "Qual é a principal função do Poder Legislativo no Brasil?"
    query_llm(prompt1)

    # Teste 2: Pedido criativo
    prompt2 = "Escreva uma frase curta e otimista sobre aprender novas tecnologias."
    query_llm(prompt2)

    # Teste 3: Pergunta sobre o próprio modelo (pode ou não saber responder)
    prompt3 = "Quem te criou?"
    query_llm(prompt3)