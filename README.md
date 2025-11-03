# Serviço de Validação de Pedidos

Um serviço Flask em Python que valida resumos de pedidos de assistentes virtuais contra um banco de dados Supabase, garantindo que todos os valores estejam corretos.

## 🎯 Objetivo

Resolver o problema de inconsistência de valores gerados por bots em plataformas como FiqOn, validando:

- ✓ Preços de produtos
- ✓ Preços de adicionais
- ✓ Taxas de entrega por bairro
- ✓ Valor total do pedido

## 🏗️ Arquitetura

```
FiqOn Bot (resumo em texto)
    ↓
Flask API
    ├─ LLM Extractor (OpenAI GPT-4.1-mini)
    │   └─ Converte texto em JSON estruturado
    └─ Order Validator
        └─ Supabase PostgreSQL
            └─ Retorna: válido ou erros + correções
```

## 📋 Pré-requisitos

- Python 3.8+
- Conta OpenAI com API key
- Projeto Supabase com tabelas configuradas
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone <seu-repositorio>
cd order_validator_service
```

### 2. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
OPENAI_API_KEY=sk-seu-api-key-aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anonima-aqui
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aleatoria
PORT=5000
HOST=0.0.0.0
```

## 📊 Estrutura do Banco de Dados

### Tabela: `produtos`

```sql
CREATE TABLE produtos (
  id SERIAL PRIMARY KEY,
  tipo VARCHAR(50),
  nome VARCHAR(255) NOT NULL,
  ingredientes TEXT,
  tamanho VARCHAR(50),
  preco NUMERIC(10, 2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Disponível',
  categoria VARCHAR(100),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `adicionais`

```sql
CREATE TABLE adicionais (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  tipo VARCHAR(50),
  tamanho VARCHAR(50),
  preco NUMERIC(10, 2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Disponível',
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `bairros`

```sql
CREATE TABLE bairros (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  taxa NUMERIC(10, 2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Disponível',
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🏃 Executar a Aplicação

### Modo Desenvolvimento

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

### Modo Produção

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📡 Endpoints

### Health Check

```bash
GET /health
```

### Validar Pedido

```bash
POST /api/validate-order
Content-Type: application/json

{
  "resumo": "Perfeito! Aqui está o RESUMO\nNOME: João Silva\n..."
}
```

### Extrair Dados (Debug)

```bash
POST /api/extract-order
Content-Type: application/json

{
  "resumo": "Perfeito! Aqui está o RESUMO\n..."
}
```

## 📖 Documentação Completa

Veja [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) para documentação detalhada de todos os endpoints, estruturas de resposta e exemplos de integração.

## 🧪 Testando a API

### Usando cURL

```bash
curl -X POST http://localhost:5000/api/validate-order \
  -H "Content-Type: application/json" \
  -d '{
    "resumo": "Perfeito! Aqui está o RESUMO\nNOME: João Silva\nTELEFONE: (62) 99999-8888\nUNIDADE: Maria Dilce\nPRODUTOS SOLICITADOS: 1 Pizza grande Calabresa Acebolada - R$ 50,00\nENDEREÇO: Rua das Flores, Qd 12 Lt 5, Vila Cristina\nTAXA DE ENTREGA: R$ 3,00\nVALOR TOTAL: R$ 53,00\nFORMA DE PAGAMENTO: Dinheiro"
  }'
```

### Usando Python

```python
import requests

response = requests.post(
    'http://localhost:5000/api/validate-order',
    json={
        'resumo': 'Seu resumo aqui...'
    }
)

print(response.json())
```

## 🔧 Configuração no Render.com

### 1. Criar Novo Serviço Web

- Conectar repositório GitHub
- Selecionar Python como linguagem
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

### 2. Adicionar Variáveis de Ambiente

No painel do Render, adicione:

```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
FLASK_ENV=production
SECRET_KEY=...
```

### 3. Deploy

O Render fará deploy automaticamente a cada push para a branch principal.

## 📝 Logs

Os logs são exibidos no console e contêm informações sobre:

- Requisições recebidas
- Extração de dados via LLM
- Validação contra banco de dados
- Erros e exceções

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY not found"

Verifique se a variável de ambiente está configurada:

```bash
echo $OPENAI_API_KEY
```

### Erro: "Falha ao conectar ao Supabase"

Verifique:
- URL do Supabase está correta
- Chave anônima está correta
- Projeto Supabase está ativo
- Tabelas existem no banco

### Erro: "Produto não encontrado"

Verifique se:
- O produto existe na tabela `produtos`
- O status é "Disponível"
- O nome corresponde exatamente (ou use normalização)

## 🔐 Segurança

- Use variáveis de ambiente para credenciais
- Nunca commit `.env` no repositório
- Use HTTPS em produção
- Implemente rate limiting se necessário
- Valide todas as entradas

## 📦 Dependências

| Pacote | Versão | Propósito |
| :--- | :--- | :--- |
| Flask | 3.0.0 | Framework web |
| Flask-CORS | 4.0.0 | Suporte CORS |
| python-dotenv | 1.0.0 | Variáveis de ambiente |
| openai | 1.3.0 | API OpenAI |
| supabase | 2.3.4 | Cliente Supabase |
| gunicorn | 21.2.0 | Servidor WSGI |
| pydantic | 2.5.0 | Validação de dados |

## 📄 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido com ❤️ para resolver problemas de validação de pedidos em assistentes virtuais.

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a [documentação da API](./API_DOCUMENTATION.md)
2. Consulte os logs da aplicação
3. Teste com o endpoint `/api/extract-order` para debug

---

**Versão:** 1.0.0  
**Última Atualização:** 2025-11-02
