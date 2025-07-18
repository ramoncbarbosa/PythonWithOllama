import os
import json
import uuid
import requests
import time

# -------- CONFIGS OLLAMA --------
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"
TIMEOUT = 60
MAX_TOKENS = 800
TEMPERATURE = 0.6

categories = [
    "variáveis",
    "listas",
    "condicionais",
    "funções",
    "comparações",
    "textos_e_caracteres",
    "números",
    "operadores_matemáticos",
    "operadores_lógicos",
]

subcategories = {
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

def generate_prompt(subcategoria):
    return f"Considere o tópico '{subcategoria}'. Gere 5 perguntas de múltipla escolha sobre esse tópico. Cada pergunta deve conter exatamente 5 opções de resposta, variadas. Inclua um campo answer_keys como array, onde cada item é a letra da resposta correta ('A', 'B', 'C', 'D' ou 'E'). Responda apenas com o JSON bruto, sem explicação e sem usar markdown. Não escreva nada além do JSON."

def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS},
        "stream": False
    }

    try:
        print(f"📡 OLLAMA-{OLLAMA_MODEL}")
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        response_json = resp.json()
        return response_json["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"🌐 Erro OLLAMA: {e}")
        return ""

def create_quiz_json(categoria, subcategoria):
    response = call_ollama(generate_prompt(subcategoria))
    quiz = json.loads(response)

    return {
        "group_id": str(uuid.uuid4()),
        "category": categoria,
        "subject": subcategoria,
        "prompt": generate_prompt(subcategoria),
        "source": "ollama",
        "questions": quiz["questions"],
        "answer_keys": quiz["answer_keys"]
    }

all_quizzes = []

for categoria in categories:
    for subcategoria in subcategories[categoria]:
        quiz_gerado = create_quiz_json(categoria, subcategoria)
        all_quizzes.append(quiz_gerado)

output_filename = "todos_quizzes_ollama.json"

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(all_quizzes, f, ensure_ascii=False, indent=4)

print(f"Todos quizzes salvos em: {output_filename}")
