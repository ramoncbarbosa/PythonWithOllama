import os
import json
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

# Configurações do Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
TIMEOUT = int(os.getenv("TIMEOUT", 60))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))

# Categorias e Subcategorias
categories = {
    "variáveis": ["o_que_são_variáveis", "tipos_existentes_de_variáveis", "variáveis_mutáveis", "escopo_local_da_variável", "escopo_global_da_variável"],
    "listas": ["o_que_são_listas", "adicionar_elemento_na_lista", "remover_elemento_da_lista", "ordenar_lista", "acessar_elemento_da_lista"],
    "condicionais": ["o_que_são_condicionais", "condicional_simples", "condicional_composta", "condicional_aninhada"],
    "funções": ["o_que_são_funções", "como_usar_funções", "tipos_de_funções"],
    "comparações": ["comparação_entre_valores", "maior_ou_menor", "comparação_de_conteúdo", "impacto_da_comparação"],
    "textos_e_caracteres": ["o_que_são_textos", "operações_de_concatenacao_de_textos", "o_que_são_caracteres", "como_converter_caracteres"],
    "números": ["o_que_são_números_inteiros", "o_que_são_números_decimais"],
    "operadores_matemáticos": ["operadores_matemáticos_básicos"],
    "operadores_lógicos": ["o_que_são_operadores_lógicos"],
}

# Geração do Prompt
def generate_prompt(subcategoria):
    return (
        f"Considere o tópico '{subcategoria}'. "
        "Gere 5 perguntas de múltipla escolha sobre esse tópico. "
        "Cada pergunta deve conter exatamente 5 opções de resposta, variadas. "
        "Inclua um campo answer_keys como array, onde cada item é a letra da resposta correta ('A', 'B', 'C', 'D' ou 'E'). "
        "Responda apenas com o JSON bruto, sem explicação e sem usar markdown. Não escreva nada além do JSON. "
        "Formato de resposta esperado: "
        '{{"questions": ['
        '{{"question": "Pergunta 1", "options": ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]}},'
        '{{"question": "Pergunta 2", "options": ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]}},'
        '{{"question": "Pergunta 3", "options": ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]}},'
        '{{"question": "Pergunta 4", "options": ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]}},'
        '{{"question": "Pergunta 5", "options": ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]}}'
        '], "answer_keys": ["A", "B", "C", "D", "E"]}}'
    )


# Chamada à API do Ollama
def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS},
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"❌ Erro na chamada à API do Ollama: {e}")
        return None

# Geração dos quizzes completos
all_quizzes = []

for categoria, subcats in categories.items():
    for subcategoria in subcats:
        print(f"\n📚 Gerando quiz para: {categoria}/{subcategoria}")
        prompt = generate_prompt(subcategoria)
        raw_response = call_ollama(prompt)

        if raw_response is None:
            print("⚠️ Resposta vazia ou erro de conexão.")
            continue

        try:
            quiz = json.loads(raw_response)

            if "questions" in quiz and "answer_keys" in quiz:
                all_quizzes.append({
                    "group_id": str(uuid.uuid4()),
                    "category": categoria,
                    "subject": subcategoria,
                    "prompt": prompt,
                    "source": "ollama",
                    "questions": quiz["questions"],
                    "answer_keys": quiz["answer_keys"]
                })
            else:
                print("⚠️ Resposta inválida, faltam campos esperados. Resposta parcial:")
                print(json.dumps(quiz, indent=2)[:1000])  # Limita a 1000 caracteres

        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao decodificar JSON: {e}")
            print("📝 Conteúdo recebido:")
            print(raw_response[:1000])  # Limita o print

# Salvar o resultado
with open("quizzes.json", 'w', encoding='utf-8') as f:
    json.dump(all_quizzes, f, ensure_ascii=False, indent=4)

print("\n✅ Quizzes salvos em quizzes.json")
