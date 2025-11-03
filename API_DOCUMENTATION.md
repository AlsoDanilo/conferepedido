# Documentação da API - Serviço de Validação de Pedidos

## Visão Geral

O **Serviço de Validação de Pedidos** é uma API Flask que recebe resumos de pedidos em texto livre, extrai dados estruturados usando LLM (OpenAI) e valida os valores contra um banco de dados Supabase.

A solução resolve o problema de inconsistência de valores gerados por assistentes virtuais, garantindo que todos os preços estejam corretos antes de processar o pedido.

---

## Arquitetura

```
FiqOn (Bot) 
    ↓ (resumo em texto)
Flask API
    ├─ LLM Extractor (OpenAI)
    │   └─ Estrutura JSON
    └─ Order Validator
        └─ Supabase (produtos, adicionais, bairros)
            └─ Resultado: válido ou erros + correções
```

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Descrição:** Verifica se o serviço está operacional.

**Response (200):**
```json
{
  "status": "ok",
  "service": "Order Validator Service",
  "version": "1.0.0"
}
```

---

### 2. Validar Pedido (Principal)

**Endpoint:** `POST /api/validate-order`

**Descrição:** Recebe um resumo de pedido, extrai dados via LLM e valida contra o banco de dados.

**Request:**
```json
{
  "resumo": "Perfeito! Aqui está o RESUMO\nNOME: João Silva\nTELEFONE: (62) 99999-8888\nUNIDADE: Maria Dilce\nPRODUTOS SOLICITADOS: 1 Pizza grande Calabresa Acebolada - R$ 50,00\n1 Pizza pequena Mussarela - R$ 27,00\nENDEREÇO: Rua das Flores, Qd 12 Lt 5, Vila Cristina\nTAXA DE ENTREGA: R$ 3,00\nVALOR TOTAL: R$ 80,00\nFORMA DE PAGAMENTO: Dinheiro\nTROCO: Para R$ 100,00\nOBSERVAÇÕES: Sem cebola na pizza pequena"
}
```

**Response (200) - Pedido Válido:**
```json
{
  "status": "sucesso",
  "pedido_valido": true,
  "dados_extraidos": {
    "nome": "João Silva",
    "telefone": "6299999888",
    "unidade": "Maria Dilce",
    "produtos": [
      {
        "nome": "Pizza grande Calabresa Acebolada",
        "preco": 50
      },
      {
        "nome": "Pizza pequena Mussarela",
        "preco": 27
      }
    ],
    "endereco": "Rua das Flores, Qd 12 Lt 5, Vila Cristina",
    "bairro": "Vila Cristina",
    "taxa_entrega": 3,
    "valor_total": 80,
    "forma_pagamento": "Dinheiro",
    "troco": 100,
    "observacoes": "Sem cebola na pizza pequena",
    "tipo_entrega": "entrega"
  },
  "validacao": {
    "valor_total_informado": 80,
    "valor_total_calculado": 80,
    "diferenca": 0,
    "erros": [],
    "correcoes": [],
    "resumo": "✓ Pedido validado com sucesso! Todos os valores estão corretos."
  }
}
```

**Response (200) - Pedido com Erros:**
```json
{
  "status": "sucesso",
  "pedido_valido": false,
  "dados_extraidos": {
    "nome": "João Silva",
    "telefone": "6299999888",
    "unidade": "Maria Dilce",
    "produtos": [
      {
        "nome": "Pizza grande Calabresa Acebolada",
        "preco": 50
      },
      {
        "nome": "Pizza pequena Mussarela",
        "preco": 28
      }
    ],
    "endereco": "Rua das Flores, Qd 12 Lt 5, Vila Cristina",
    "bairro": "Vila Cristina",
    "taxa_entrega": 3,
    "valor_total": 81,
    "forma_pagamento": "Dinheiro",
    "troco": 100,
    "observacoes": "Sem cebola na pizza pequena",
    "tipo_entrega": "entrega"
  },
  "validacao": {
    "valor_total_informado": 81,
    "valor_total_calculado": 80,
    "diferenca": -1,
    "erros": [
      "Preço incorreto para 'Pizza pequena Mussarela': informado R$ 28,00, correto R$ 27,00",
      "Valor total incorreto: informado R$ 81,00, calculado R$ 80,00"
    ],
    "correcoes": [
      {
        "produto": "Pizza pequena Mussarela",
        "preco_informado": 28,
        "preco_correto": 27,
        "diferenca": -1
      },
      {
        "valor_informado": 81,
        "valor_calculado": 80,
        "diferenca": -1
      }
    ],
    "resumo": "✗ Pedido contém erros:\n\n1. Preço incorreto para 'Pizza pequena Mussarela': informado R$ 28,00, correto R$ 27,00\n2. Valor total incorreto: informado R$ 81,00, calculado R$ 80,00\n\nCorreções necessárias:\n- Pizza pequena Mussarela: R$ 27,00\n- Valor total correto: R$ 80,00\n"
  }
}
```

**Response (400) - Erro de Validação:**
```json
{
  "erro": "Campo \"resumo\" é obrigatório",
  "status": "erro"
}
```

**Response (500) - Erro Interno:**
```json
{
  "erro": "Erro interno do servidor: [detalhes do erro]",
  "status": "erro"
}
```

---

### 3. Extrair Dados (Debug)

**Endpoint:** `POST /api/extract-order`

**Descrição:** Apenas extrai dados do resumo sem validação. Útil para debug e testes.

**Request:**
```json
{
  "resumo": "Texto do resumo do pedido..."
}
```

**Response (200):**
```json
{
  "status": "sucesso",
  "dados": {
    "nome": "João Silva",
    "telefone": "6299999888",
    "unidade": "Maria Dilce",
    "produtos": [...],
    "endereco": "...",
    "bairro": "...",
    "taxa_entrega": 3,
    "valor_total": 80,
    "forma_pagamento": "Dinheiro",
    "troco": 100,
    "observacoes": "...",
    "tipo_entrega": "entrega"
  }
}
```

---

## Códigos de Status HTTP

| Código | Significado |
| :--- | :--- |
| `200` | Sucesso - Requisição processada |
| `400` | Bad Request - Dados inválidos ou incompletos |
| `404` | Not Found - Rota não encontrada |
| `500` | Internal Server Error - Erro no servidor |

---

## Estrutura de Resposta da Validação

### Campo: `validacao`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `valor_total_informado` | `number` | Valor total informado no resumo |
| `valor_total_calculado` | `number` | Valor total calculado pela validação |
| `diferenca` | `number` | Diferença entre informado e calculado |
| `erros` | `array` | Lista de erros encontrados |
| `correcoes` | `array` | Lista de correções necessárias |
| `resumo` | `string` | Resumo legível da validação |

### Estrutura de Correção

**Para Produtos:**
```json
{
  "produto": "Pizza pequena Mussarela",
  "preco_informado": 28,
  "preco_correto": 27,
  "diferenca": -1
}
```

**Para Taxa de Entrega:**
```json
{
  "bairro": "Vila Cristina",
  "taxa_informada": 4,
  "taxa_correta": 3,
  "diferenca": -1
}
```

**Para Valor Total:**
```json
{
  "valor_informado": 81,
  "valor_calculado": 80,
  "diferenca": -1
}
```

---

## Fluxo de Integração com FiqOn

### Passo 1: Preparar Resumo
O bot do FiqOn gera o resumo do pedido no formato estruturado (Modelo 1 ou 2).

### Passo 2: Enviar para Validação
```bash
curl -X POST https://seu-servico.render.com/api/validate-order \
  -H "Content-Type: application/json" \
  -d '{
    "resumo": "Perfeito! Aqui está o RESUMO\n..."
  }'
```

### Passo 3: Processar Resposta
- **Se `pedido_valido` = `true`:** Processar pedido normalmente
- **Se `pedido_valido` = `false`:** Exibir erros e correções ao cliente ou ao operador

---

## Variáveis de Ambiente Necessárias

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=eyJhbGc...

# Flask
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta

# Server
PORT=5000
HOST=0.0.0.0
```

---

## Tratamento de Erros

### Erro: "Produto não encontrado no cardápio"
**Causa:** O produto extraído não existe na tabela `produtos` ou está com status "indisponível".

**Solução:** Verificar se o nome do produto está correto no banco de dados.

### Erro: "Bairro não encontrado ou indisponível"
**Causa:** O bairro não existe na tabela `bairros` ou está com status "indisponível".

**Solução:** Adicionar o bairro à tabela ou ativar seu status.

### Erro: "Preço incorreto"
**Causa:** O preço informado no resumo não coincide com o preço no banco de dados.

**Solução:** Usar o preço sugerido na resposta de correção.

---

## Performance e Limites

- **Timeout de Requisição:** 30 segundos
- **Tamanho Máximo de Resumo:** 5000 caracteres
- **Taxa de Requisições:** Sem limite (depende do plano OpenAI)

---

## Exemplo de Integração em Python

```python
import requests

def validar_pedido(resumo):
    """Valida um pedido usando o serviço."""
    
    url = "https://seu-servico.render.com/api/validate-order"
    
    payload = {
        "resumo": resumo
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        resultado = response.json()
        
        if resultado['pedido_valido']:
            print("✓ Pedido válido!")
            return True
        else:
            print("✗ Pedido com erros:")
            for erro in resultado['validacao']['erros']:
                print(f"  - {erro}")
            return False
    else:
        print(f"Erro: {response.status_code}")
        return False

# Uso
resumo = "Perfeito! Aqui está o RESUMO\n..."
validar_pedido(resumo)
```

---

## Suporte e Debugging

Para debug, use o endpoint `/api/extract-order` para verificar se os dados estão sendo extraídos corretamente antes de validar.

Verifique os logs da aplicação para mais detalhes sobre erros.

---

**Versão:** 1.0.0  
**Última Atualização:** 2025-11-02
