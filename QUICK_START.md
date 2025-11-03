# Guia de Início Rápido

Siga este guia para colocar o serviço em funcionamento em menos de 10 minutos.

## ⚡ Passo 1: Clonar e Configurar (2 min)

```bash
# Clonar repositório
git clone <seu-repositorio>
cd order_validator_service

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## 🔑 Passo 2: Configurar Credenciais (3 min)

1. Copie `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edite `.env` com suas credenciais:
   ```env
   OPENAI_API_KEY=sk-seu-api-key-aqui
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_KEY=sua-chave-anonima-aqui
   SECRET_KEY=gere-uma-chave-aleatoria-aqui
   ```

   **Como obter as credenciais:**
   - **OPENAI_API_KEY:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - **SUPABASE_URL e SUPABASE_KEY:** Dashboard do Supabase → Settings → API

## 📊 Passo 3: Criar Tabelas no Supabase (2 min)

1. Acesse seu projeto Supabase
2. Vá para **SQL Editor**
3. Cole o conteúdo de `database_schema.sql`
4. Execute o script

**Pronto!** As tabelas foram criadas com dados de exemplo.

## 🚀 Passo 4: Executar Localmente (1 min)

```bash
python app.py
```

Você verá:
```
 * Running on http://localhost:5000
```

## ✅ Passo 5: Testar (2 min)

Em outro terminal:

```bash
python test_api.py
```

Você verá um relatório de testes:
```
✓ Health Check
✓ Extração de Dados
✓ Pedido Válido
✓ Pedido com Erro
✓ Retirada na Loja
✓ Requisição Inválida

Taxa de sucesso: 100%
```

## 🌐 Passo 6: Deploy no Render (2 min)

1. Faça push do código para GitHub
2. Acesse [render.com](https://render.com)
3. Clique em **New +** → **Web Service**
4. Conecte seu repositório GitHub
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
6. Adicione as variáveis de ambiente (mesmas do `.env`)
7. Clique em **Create Web Service**

Pronto! Seu serviço estará disponível em:
```
https://seu-servico.render.com
```

## 🔗 Passo 7: Integrar com FiqOn

No seu fluxo FiqOn, adicione um bloco HTTP:

```
POST https://seu-servico.render.com/api/validate-order
Content-Type: application/json

{
  "resumo": "{{variavel_com_resumo}}"
}
```

Processe a resposta:
- Se `pedido_valido` = `true`: Confirmar pedido
- Se `pedido_valido` = `false`: Exibir erros

## 📖 Documentação Completa

Para mais detalhes, consulte:

- [README.md](./README.md) - Documentação completa
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Referência de endpoints
- [FIQON_INTEGRATION.md](./FIQON_INTEGRATION.md) - Guia de integração com FiqOn

## 🆘 Troubleshooting Rápido

| Problema | Solução |
| :--- | :--- |
| `ModuleNotFoundError` | Execute `pip install -r requirements.txt` |
| `OPENAI_API_KEY not found` | Verifique se `.env` está configurado |
| `Falha ao conectar ao Supabase` | Verifique URL e chave no `.env` |
| `Produto não encontrado` | Adicione o produto na tabela `produtos` |
| `Bairro não encontrado` | Adicione o bairro na tabela `bairros` |

## 📞 Próximos Passos

1. ✅ Testar localmente
2. ✅ Deploy no Render
3. ✅ Integrar com FiqOn
4. ✅ Monitorar logs
5. ✅ Ajustar conforme necessário

---

**Tempo Total:** ~10 minutos  
**Dificuldade:** Iniciante  
**Suporte:** Consulte a documentação completa
