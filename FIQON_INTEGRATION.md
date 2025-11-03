# Guia de Integração com FiqOn

Este documento descreve como integrar o **Serviço de Validação de Pedidos** com seu fluxo no FiqOn.

## 📋 Visão Geral

O serviço atua como um **middleware de validação** entre o bot do FiqOn e o processamento do pedido. Após o bot gerar o resumo do pedido, você envia para validação antes de confirmar o pedido.

```
FiqOn Bot
  ↓ (gera resumo)
Resumo em Texto
  ↓ (envia para validação)
Serviço Flask
  ├─ Extrai dados com LLM
  └─ Valida contra Supabase
  ↓ (retorna resultado)
Resultado: Válido ou Erros
  ↓
FiqOn (processa ou corrige)
```

## 🔗 Passo 1: Obter URL do Serviço

Após fazer deploy no Render.com, você receberá uma URL como:

```
https://seu-servico.render.com
```

Guarde esta URL, você precisará dela no FiqOn.

## 🔌 Passo 2: Configurar Webhook no FiqOn

No FiqOn, configure um webhook ou integração HTTP para chamar o serviço:

### Opção A: Usando Bloco HTTP (Recomendado)

1. No seu fluxo, após o bot gerar o resumo, adicione um **bloco HTTP**
2. Configure:
   - **Método:** POST
   - **URL:** `https://seu-servico.render.com/api/validate-order`
   - **Headers:**
     ```
     Content-Type: application/json
     ```
   - **Body:**
     ```json
     {
       "resumo": "{{variavel_com_resumo}}"
     }
     ```

3. Mapeie a variável `{{variavel_com_resumo}}` para o resumo gerado pelo bot

### Opção B: Usando Integração Customizada

Se o FiqOn suporta integrações customizadas:

1. Acesse as configurações de integrações
2. Adicione uma nova integração HTTP
3. Configure com os mesmos parâmetros acima

## 📊 Passo 3: Processar Resposta

A resposta do serviço terá a seguinte estrutura:

```json
{
  "status": "sucesso",
  "pedido_valido": true/false,
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

### Se `pedido_valido` = `true`

Prossiga com o processamento normal do pedido:

```
Fluxo FiqOn
  ├─ Confirmar pedido
  ├─ Enviar para cozinha
  ├─ Registrar no sistema
  └─ Informar ao cliente
```

### Se `pedido_valido` = `false`

Exiba os erros e correções ao cliente ou operador:

```
Fluxo FiqOn
  ├─ Exibir mensagem: "Encontramos erros no seu pedido"
  ├─ Listar erros de: validacao.erros
  ├─ Sugerir correções de: validacao.correcoes
  ├─ Oferecer opções:
  │   ├─ Aceitar correções sugeridas
  │   ├─ Editar pedido manualmente
  │   └─ Cancelar pedido
  └─ Revalidar se necessário
```

## 💬 Passo 4: Mensagens para o Cliente

### Pedido Válido

```
✓ Perfeito! Seu pedido foi validado com sucesso.
  
Resumo:
- Valor total: R$ 80,00
- Forma de pagamento: Dinheiro
- Entrega em: Vila Cristina

Deseja confirmar?
```

### Pedido com Erros

```
⚠️ Encontramos alguns erros no seu pedido:

{{validacao.resumo}}

Deseja aceitar as correções sugeridas?
- Sim, aceitar correções
- Não, editar manualmente
- Cancelar pedido
```

## 🔄 Passo 5: Fluxo Completo no FiqOn

Aqui está um exemplo de fluxo completo:

```
1. Bot coleta informações do cliente
   ├─ Nome
   ├─ Telefone
   ├─ Produtos
   ├─ Endereço/Bairro
   └─ Forma de pagamento

2. Bot gera resumo estruturado
   └─ Armazena em variável: {{resumo_pedido}}

3. Bloco HTTP chama validação
   ├─ POST /api/validate-order
   ├─ Body: {"resumo": "{{resumo_pedido}}"}
   └─ Armazena resposta em: {{resultado_validacao}}

4. Decisão: {{resultado_validacao.pedido_valido}}
   ├─ Se TRUE:
   │   ├─ Exibir: "Pedido validado!"
   │   ├─ Processar pedido
   │   └─ Enviar confirmação
   │
   └─ Se FALSE:
       ├─ Exibir: "Erros encontrados"
       ├─ Listar: {{resultado_validacao.validacao.erros}}
       ├─ Sugerir: {{resultado_validacao.validacao.correcoes}}
       └─ Oferecer opções de correção
```

## 🧪 Passo 6: Testar a Integração

### Teste Manual no FiqOn

1. Inicie o fluxo do bot
2. Preencha as informações do pedido
3. Verifique se o resumo é gerado corretamente
4. Confirme a validação

### Teste com cURL (para debug)

```bash
curl -X POST https://seu-servico.render.com/api/validate-order \
  -H "Content-Type: application/json" \
  -d '{
    "resumo": "Perfeito! Aqui está o RESUMO\nNOME: João Silva\n..."
  }'
```

### Monitorar Logs

No Render.com, acesse os logs para ver:

- Requisições recebidas
- Extração de dados
- Validação contra banco
- Erros (se houver)

## 🔐 Passo 7: Segurança

### Variáveis de Ambiente

Certifique-se de que as credenciais estão configuradas no Render:

- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SECRET_KEY`

### CORS

O serviço está configurado para aceitar requisições de qualquer origem. Se necessário, restrinja em `app.py`:

```python
CORS(app, resources={r"/api/*": {"origins": ["https://seu-fiqon.com"]}})
```

### Rate Limiting

Se receber muitas requisições, implemente rate limiting:

```bash
pip install Flask-Limiter
```

## 📞 Troubleshooting

### Erro: "Connection refused"

- Verifique se o serviço está rodando
- Confirme a URL está correta
- Teste com `/health`

### Erro: "Invalid JSON response"

- Verifique o formato do resumo enviado
- Confirme que o campo "resumo" está presente
- Teste com `/api/extract-order` para debug

### Erro: "Produto não encontrado"

- Verifique se o produto existe no Supabase
- Confirme o status é "Disponível"
- Verifique a normalização de nomes

### Erro: "Bairro não encontrado"

- Adicione o bairro à tabela `bairros`
- Confirme o status é "Disponível"
- Verifique a escrita do nome

## 📈 Monitoramento

### Métricas Importantes

- Taxa de pedidos válidos vs inválidos
- Tipos de erros mais comuns
- Tempo de resposta da validação
- Taxa de sucesso da extração LLM

### Dashboard Sugerido

Crie um dashboard no Supabase para monitorar:

```sql
-- Pedidos validados por dia
SELECT DATE(criado_em) as data, COUNT(*) as total
FROM pedidos_validados
GROUP BY DATE(criado_em)
ORDER BY data DESC;

-- Erros mais comuns
SELECT erro, COUNT(*) as total
FROM pedidos_com_erro
GROUP BY erro
ORDER BY total DESC;
```

## 🚀 Próximos Passos

1. **Deploy:** Faça deploy no Render.com
2. **Testes:** Execute testes com dados reais
3. **Monitoramento:** Configure alertas para erros
4. **Otimização:** Ajuste prompts e validações conforme necessário
5. **Escalabilidade:** Aumente workers se necessário

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [README do Projeto](./README.md)
- [Documentação Render.com](https://render.com/docs)
- [Documentação Supabase](https://supabase.com/docs)
- [Documentação OpenAI](https://platform.openai.com/docs)

---

**Versão:** 1.0.0  
**Última Atualização:** 2025-11-02
