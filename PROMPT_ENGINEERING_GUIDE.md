# Guia de Prompt Engineering - Como Funciona o "Assistente"

## A Pergunta: Como a OpenAI Sabe Qual é o Assistente?

**Resposta Curta:** A OpenAI **não sabe** automaticamente. **Você define** o assistente através do **prompt** que envia.

---

## 🎯 Conceito Fundamental

Não existe um "assistente" pré-existente na OpenAI. O que existe é:

1. **Um modelo de linguagem** (GPT-4.1-mini)
2. **Um prompt** que você envia (instruções)
3. **Parâmetros de controle** (temperature, max_tokens)

Juntos, eles **criam o comportamento** do "assistente".

---

## 📊 Estrutura da Requisição

Toda requisição para OpenAI tem esta estrutura:

```python
response = self.client.chat.completions.create(
    model="gpt-4.1-mini",           # ← O modelo base
    messages=[
        {
            "role": "system",
            "content": "Instruções do sistema"  # ← Define o comportamento
        },
        {
            "role": "user",
            "content": "Sua tarefa/pergunta"    # ← O que fazer
        }
    ],
    temperature=0.2,                # ← Como responder (0=determinístico, 1=criativo)
    max_tokens=1500                 # ← Limite de resposta
)
```

---

## 🔍 Os 3 Componentes

### 1. System Message (Define o Assistente)

```python
{
    "role": "system",
    "content": "Você é um assistente especializado em extração de dados de resumos de pedidos. Retorne APENAS um JSON válido, sem explicações adicionais."
}
```

**O que faz:**
- Define a **personalidade** do modelo
- Define a **especialização** (extração de dados)
- Define o **comportamento** (retornar APENAS JSON)

**Exemplos de diferentes "assistentes":**

```python
# Assistente 1: Extrator rigoroso
"Você é um especialista EXTREMAMENTE rigoroso em extração de dados. Se algum dado estiver incompleto, retorne um erro."

# Assistente 2: Extrator flexível
"Você é um assistente flexível em extração de dados. Se um campo não estiver disponível, use null."

# Assistente 3: Validador
"Você é um especialista em validação de dados. Verifique se todos os preços são números válidos."

# Assistente 4: Corretor
"Você é um especialista em correção de dados. Corrija erros de digitação e normalize os dados."
```

### 2. User Message (A Tarefa)

```python
{
    "role": "user",
    "content": """
Analise o seguinte resumo de pedido e extraia os dados em formato JSON estruturado.

RESUMO DO PEDIDO:
Perfeito! Aqui está o RESUMO
NOME: João Silva
TELEFONE: (62) 99999-8888
...

Extraia os seguintes dados:
- nome: Nome do cliente
- telefone: Telefone sem formatação
...

Retorne APENAS um JSON válido com a seguinte estrutura:
{
  "nome": "string",
  "telefone": "string",
  ...
}
"""
}
```

**O que faz:**
- Fornece o **contexto** (resumo do pedido)
- Fornece as **instruções específicas** (quais dados extrair)
- Fornece o **formato esperado** (estrutura JSON)

### 3. Parâmetros de Controle

```python
temperature=0.2,      # Baixo = determinístico, Alto = criativo
max_tokens=1500       # Limite de resposta
```

**Temperature:**
- `0.0` → Sempre a mesma resposta (determinístico)
- `0.5` → Meio termo
- `1.0` → Muito variável (criativo)

Para extração de dados, usamos `0.2` (baixo) porque queremos **consistência**.

---

## 🔄 Fluxo Completo

```
1. Seu código chama OpenAI
   ↓
2. Envia:
   - System Message: "Você é especialista em extração"
   - User Message: "Extraia dados deste resumo"
   - Parâmetros: temperature=0.2
   ↓
3. OpenAI processa:
   - Lê system message
   - Entende que é um "assistente de extração"
   - Lê user message
   - Processa o resumo
   - Gera JSON estruturado
   ↓
4. Retorna resposta
   ↓
5. Seu código parseia e valida
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Mesmo Modelo, Diferentes "Assistentes"

```python
# Assistente 1: Extrator
system_message_1 = "Você é um especialista em extração de dados. Retorne APENAS JSON."
response_1 = openai.ChatCompletion.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": system_message_1},
        {"role": "user", "content": "Extraia dados deste resumo..."}
    ]
)
# Retorna: {"nome": "João", "telefone": "62999998888", ...}

# Assistente 2: Validador
system_message_2 = "Você é um especialista em validação. Verifique se os dados estão corretos."
response_2 = openai.ChatCompletion.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": system_message_2},
        {"role": "user", "content": "Valide estes dados..."}
    ]
)
# Retorna: {"valido": true, "erros": [], ...}

# Assistente 3: Corretor
system_message_3 = "Você é um especialista em correção de dados. Corrija erros e normalize."
response_3 = openai.ChatCompletion.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": system_message_3},
        {"role": "user", "content": "Corrija estes dados..."}
    ]
)
# Retorna: {"nome": "João Silva", "telefone": "6299999888", ...}
```

**O mesmo modelo (GPT-4.1-mini) se comporta como 3 "assistentes" diferentes!**

---

### Exemplo 2: Customizando o Prompt

No seu código (`llm_extractor.py`), você pode customizar o prompt:

**Versão Atual (Simples):**
```python
def _build_extraction_prompt(self, order_summary: str) -> str:
    return f"""
Analise o seguinte resumo de pedido e extraia os dados em formato JSON estruturado.

RESUMO DO PEDIDO:
{order_summary}

Extraia os seguintes dados:
- nome: Nome do cliente
- telefone: Telefone sem formatação
...
"""
```

**Versão Melhorada (Com Validação):**
```python
def _build_extraction_prompt(self, order_summary: str) -> str:
    return f"""
Analise o seguinte resumo de pedido e extraia os dados em formato JSON estruturado.

REGRAS IMPORTANTES:
1. Se um preço estiver inválido, marque como "preco_invalido": true
2. Se um telefone estiver incompleto, marque como "telefone_incompleto": true
3. Se um bairro não estiver na lista padrão, marque como "bairro_nao_padrao": true

RESUMO DO PEDIDO:
{order_summary}

Extraia os seguintes dados:
- nome: Nome do cliente
- telefone: Telefone sem formatação
...

Retorne APENAS um JSON válido com a seguinte estrutura:
{{
  "nome": "string",
  "telefone": "string",
  "preco_invalido": boolean,
  "telefone_incompleto": boolean,
  "bairro_nao_padrao": boolean,
  ...
}}
"""
```

---

## 🎬 Analogia: O Ator

Pense em GPT-4.1-mini como um **ator versátil de cinema**:

```
GPT-4.1-mini = Ator versátil
System Message = Instruções de diretor
User Message = Roteiro
Temperature = Liberdade criativa
```

**Cenário 1: Sem direção**
```
Diretor: "Faça algo"
Ator: "O quê? Dança? Canto? Drama?"
```

**Cenário 2: Com direção clara**
```
Diretor: "Você é um analista de dados. Analise este documento e extraia informações em JSON."
Ator: "Entendi! Vou analisar e estruturar em JSON."
```

**Cenário 3: Mudando o papel**
```
Diretor: "Agora você é um validador. Verifique se os dados estão corretos."
Ator: "Ok, vou validar e retornar erros."
```

**Mesmo ator, papéis diferentes!**

---

## 🔧 Como Customizar para Seus Casos

### Caso 1: Extrair com Mais Detalhes

```python
system_message = """
Você é um especialista em extração de dados de pedidos de pizzaria.
Retorne APENAS um JSON válido.
Seja EXTREMAMENTE preciso com preços e quantidades.
"""
```

### Caso 2: Detectar Erros

```python
system_message = """
Você é um especialista em detecção de erros em pedidos.
Identifique:
- Preços inconsistentes
- Produtos duplicados
- Quantidades inválidas
Retorne um JSON com lista de erros encontrados.
"""
```

### Caso 3: Corrigir Dados

```python
system_message = """
Você é um especialista em limpeza e normalização de dados.
Corrija:
- Nomes com erros de digitação
- Telefones com formatação inconsistente
- Endereços incompletos
Retorne os dados corrigidos em JSON.
"""
```

---

## 📈 Boas Práticas

### ✅ Faça

```python
# Claro e específico
"Você é um especialista em extração de dados de pedidos. Retorne APENAS um JSON válido."

# Com exemplos
"Extraia o telefone sem formatação. Exemplo: (62) 99999-8888 → 6299999888"

# Com restrições
"Retorne APENAS um JSON. Sem explicações, sem markdown, sem comentários."
```

### ❌ Não Faça

```python
# Vago
"Processe este texto"

# Ambíguo
"Extraia os dados"

# Sem formato esperado
"Dê-me as informações do pedido"
```

---

## 🎯 Resumo

| Conceito | Explicação |
| :--- | :--- |
| **Assistente** | Não é pré-existente, é criado pelo prompt |
| **System Message** | Define a personalidade e especialização |
| **User Message** | Define a tarefa específica |
| **Parâmetros** | Controlam como o modelo responde |
| **Prompt Engineering** | Arte de escrever prompts eficazes |
| **Temperature** | Controla criatividade (0=determinístico, 1=criativo) |

---

## 🚀 Conclusão

A OpenAI é **extremamente flexível**. Você não precisa de um "assistente pré-existente" - você **cria o comportamento** através do prompt.

Se quiser um comportamento diferente, basta **mudar o prompt**. É assim que funciona! 💪

---

**Versão:** 1.0.0  
**Data:** 2025-11-02
