# Estrutura do Projeto

Visão geral da organização dos arquivos e responsabilidades de cada componente.

```
order_validator_service/
├── app.py                      # Aplicação Flask principal
├── config.py                   # Configurações (dev/prod)
├── llm_extractor.py           # Integração com OpenAI LLM
├── database.py                # Integração com Supabase
├── test_api.py                # Suite de testes
├── requirements.txt           # Dependências Python
├── .env.example               # Template de variáveis de ambiente
├── .env                       # Variáveis de ambiente (não commitar)
├── .gitignore                 # Arquivos ignorados pelo Git
├── render.yaml                # Configuração para deploy Render
├── database_schema.sql        # Script SQL para criar tabelas
│
├── README.md                  # Documentação principal
├── QUICK_START.md            # Guia de início rápido
├── API_DOCUMENTATION.md      # Referência completa de endpoints
├── FIQON_INTEGRATION.md      # Guia de integração com FiqOn
├── PROJECT_STRUCTURE.md      # Este arquivo
│
└── venv/                      # Ambiente virtual (não commitar)
```

## 📄 Descrição dos Arquivos

### Código Principal

#### `app.py`
**Responsabilidade:** Aplicação Flask principal  
**Componentes:**
- Inicialização da aplicação
- Configuração de CORS
- Endpoints HTTP:
  - `GET /health` - Health check
  - `POST /api/validate-order` - Validação completa
  - `POST /api/extract-order` - Extração apenas (debug)
- Error handlers

**Fluxo:**
```
Requisição HTTP
  ↓
Validação de entrada
  ↓
LLMExtractor.extract_order_data()
  ↓
OrderValidator.validate_order()
  ↓
Resposta JSON
```

#### `config.py`
**Responsabilidade:** Gerenciamento de configurações  
**Classes:**
- `Config` - Configurações base
- `DevelopmentConfig` - Configurações para desenvolvimento
- `ProductionConfig` - Configurações para produção

**Variáveis:**
- OpenAI API key e modelo
- Supabase URL e chave
- Flask environment e debug mode
- Server host e port

#### `llm_extractor.py`
**Responsabilidade:** Extração de dados estruturados usando LLM  
**Classe:** `LLMExtractor`

**Métodos principais:**
- `extract_order_data(order_summary)` - Extrai JSON do resumo
- `_build_extraction_prompt(order_summary)` - Constrói prompt para LLM

**Fluxo:**
```
Resumo em texto
  ↓
Construir prompt
  ↓
Chamar OpenAI API
  ↓
Parsear JSON
  ↓
Retornar dados estruturados
```

#### `database.py`
**Responsabilidade:** Integração com Supabase e validação de dados  
**Classes:**
- `SupabaseClient` - Cliente para Supabase
- `OrderValidator` - Validação de pedidos

**Métodos principais:**
- `get_product_by_name_and_size()` - Busca produto
- `get_neighborhood_tax()` - Busca taxa de entrega
- `get_additional_by_name_and_size()` - Busca adicional
- `validate_order()` - Valida pedido completo
- `_normalize_text()` - Normaliza texto para comparação

**Fluxo de Validação:**
```
Dados extraídos
  ├─ Validar produtos
  ├─ Validar taxa de entrega
  ├─ Validar valor total
  └─ Compilar erros e correções
```

#### `test_api.py`
**Responsabilidade:** Suite de testes da API  
**Testes:**
1. Health check
2. Extração de dados
3. Pedido válido
4. Pedido com erro
5. Retirada na loja
6. Requisição inválida

**Execução:**
```bash
python test_api.py
```

### Configuração

#### `requirements.txt`
Lista de dependências Python com versões específicas.

#### `.env.example`
Template para variáveis de ambiente. Copie para `.env` e preencha.

#### `.gitignore`
Arquivos e pastas ignorados pelo Git (venv, .env, __pycache__, etc).

#### `render.yaml`
Configuração para deploy automático no Render.com.

### Banco de Dados

#### `database_schema.sql`
Script SQL completo para criar as tabelas no Supabase:
- `bairros` - Bairros de entrega
- `adicionais` - Adicionais e bebidas
- `produtos` - Produtos do cardápio

Inclui:
- Definição de colunas
- Índices para performance
- Dados de exemplo
- Constraints e validações

### Documentação

#### `README.md`
Documentação principal do projeto com:
- Objetivo
- Arquitetura
- Pré-requisitos
- Instalação
- Execução
- Testes
- Deploy
- Troubleshooting

#### `QUICK_START.md`
Guia rápido para começar em 10 minutos.

#### `API_DOCUMENTATION.md`
Referência completa de endpoints:
- Descrição detalhada
- Exemplos de requisição/resposta
- Códigos de status HTTP
- Estrutura de resposta
- Tratamento de erros

#### `FIQON_INTEGRATION.md`
Guia específico para integração com FiqOn:
- Visão geral
- Configuração de webhook
- Processamento de resposta
- Fluxo completo
- Testes
- Monitoramento

#### `PROJECT_STRUCTURE.md`
Este arquivo - descrição da organização do projeto.

## 🔄 Fluxo de Dados

### Fluxo Completo de Validação

```
1. FiqOn Bot gera resumo
   └─ "Perfeito! Aqui está o RESUMO\n..."

2. Requisição HTTP POST
   └─ /api/validate-order
   └─ {"resumo": "..."}

3. Flask recebe e valida entrada
   └─ Verifica se "resumo" está presente

4. LLMExtractor extrai dados
   └─ Chama OpenAI GPT-4.1-mini
   └─ Retorna JSON estruturado

5. OrderValidator valida dados
   ├─ Busca produtos em Supabase
   ├─ Busca taxas de entrega
   ├─ Compara preços
   └─ Calcula valor total

6. Compila resultado
   ├─ Lista de erros (se houver)
   ├─ Sugestões de correção
   └─ Resumo legível

7. Retorna resposta JSON
   └─ {"pedido_valido": true/false, ...}

8. FiqOn processa resultado
   ├─ Se válido: confirma pedido
   └─ Se inválido: exibe erros
```

## 🔐 Fluxo de Segurança

```
Variáveis de Ambiente
  ├─ OPENAI_API_KEY (não exposto)
  ├─ SUPABASE_KEY (não exposto)
  └─ SECRET_KEY (não exposto)

Requisição HTTP
  ├─ CORS habilitado
  ├─ JSON parsing seguro
  └─ Validação de entrada

Integração com Serviços
  ├─ OpenAI API (HTTPS)
  └─ Supabase (HTTPS)

Resposta
  └─ JSON seguro sem dados sensíveis
```

## 📊 Estrutura de Dados

### Entrada: Resumo de Pedido (Texto)

```
Perfeito! Aqui está o RESUMO
NOME: João Silva
TELEFONE: (62) 99999-8888
UNIDADE: Maria Dilce
PRODUTOS SOLICITADOS: 1 Pizza grande Calabresa Acebolada - R$ 50,00
1 Pizza pequena Mussarela - R$ 27,00
ENDEREÇO: Rua das Flores, Qd 12 Lt 5, Vila Cristina
TAXA DE ENTREGA: R$ 3,00
VALOR TOTAL: R$ 80,00
FORMA DE PAGAMENTO: Dinheiro
TROCO: Para R$ 100,00
OBSERVAÇÕES: Sem cebola na pizza pequena
```

### Processamento: Dados Estruturados (JSON)

```json
{
  "nome": "João Silva",
  "telefone": "6299999888",
  "unidade": "Maria Dilce",
  "produtos": [
    {"nome": "Pizza grande Calabresa Acebolada", "preco": 50},
    {"nome": "Pizza pequena Mussarela", "preco": 27}
  ],
  "endereco": "Rua das Flores, Qd 12 Lt 5, Vila Cristina",
  "bairro": "Vila Cristina",
  "taxa_entrega": 3,
  "valor_total": 80,
  "forma_pagamento": "Dinheiro",
  "troco": 100,
  "observacoes": "Sem cebola na pizza pequena",
  "tipo_entrega": "entrega"
}
```

### Saída: Resultado de Validação (JSON)

```json
{
  "status": "sucesso",
  "pedido_valido": true,
  "dados_extraidos": { ... },
  "validacao": {
    "valor_total_informado": 80,
    "valor_total_calculado": 80,
    "diferenca": 0,
    "erros": [],
    "correcoes": [],
    "resumo": "✓ Pedido validado com sucesso!"
  }
}
```

## 🔌 Integrações Externas

### OpenAI API
- **Modelo:** GPT-4.1-mini
- **Função:** Extração de dados estruturados
- **Autenticação:** API Key
- **Timeout:** 10 segundos

### Supabase PostgreSQL
- **Tabelas:** produtos, adicionais, bairros
- **Função:** Fonte de verdade para preços
- **Autenticação:** Chave anônima
- **Timeout:** 5 segundos

### Render.com
- **Plataforma:** Deploy automático
- **Linguagem:** Python
- **Servidor:** Gunicorn WSGI
- **Escalabilidade:** Auto-scaling

## 📈 Performance

### Otimizações Implementadas

1. **Índices no Banco de Dados**
   - Nome de produtos, bairros, adicionais
   - Status para filtrar disponíveis

2. **Normalização de Texto**
   - Minúsculas
   - Remoção de acentos
   - Trim de espaços

3. **Caching (Futuro)**
   - Cache de produtos
   - Cache de bairros
   - TTL de 1 hora

4. **Logging Estruturado**
   - Rastreamento de requisições
   - Detecção de erros
   - Métricas de performance

## 🧪 Testes

### Cobertura

- ✅ Health check
- ✅ Extração de dados
- ✅ Validação de produtos
- ✅ Validação de taxa de entrega
- ✅ Validação de valor total
- ✅ Tratamento de erros
- ✅ Requisições inválidas

### Executar Testes

```bash
python test_api.py
```

## 🚀 Deployment

### Render.com

1. Conectar repositório GitHub
2. Configurar variáveis de ambiente
3. Deploy automático em cada push

### Variáveis Necessárias

```
OPENAI_API_KEY
SUPABASE_URL
SUPABASE_KEY
FLASK_ENV=production
SECRET_KEY
```

## 📞 Suporte

Para dúvidas sobre a estrutura:

1. Consulte a documentação correspondente
2. Verifique os comentários no código
3. Execute os testes para debug
4. Consulte os logs da aplicação

---

**Versão:** 1.0.0  
**Última Atualização:** 2025-11-02
