"""
Módulo para extração de dados estruturados de resumos de pedidos usando LLM.
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extrai dados estruturados de resumos de pedidos usando OpenAI."""
    
    def __init__(self):
        """Inicializa o cliente OpenAI."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def extract_order_data(self, order_summary: str) -> Optional[Dict[str, Any]]:
        """
        Extrai dados estruturados de um resumo de pedido em texto livre.
        
        Args:
            order_summary: Texto do resumo do pedido
            
        Returns:
            Dicionário com dados estruturados ou None em caso de erro
        """
        try:
            prompt = self._build_extraction_prompt(order_summary)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em extração de dados de resumos de pedidos. Retorne APENAS um JSON válido, sem explicações adicionais."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content.strip()
            
            # Remove marcadores de código se presentes
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Converte para dicionário
            data = json.loads(content.strip())
            
            logger.info(f"Dados extraídos com sucesso: {data.get('nome', 'desconhecido')}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair dados com LLM: {e}")
            return None
    
    def _build_extraction_prompt(self, order_summary: str) -> str:
        """
        Constrói o prompt para extração de dados.
        
        Args:
            order_summary: Texto do resumo do pedido
            
        Returns:
            Prompt formatado para o LLM
        """
        return f"""
Analise o seguinte resumo de pedido e extraia os dados em formato JSON estruturado.

RESUMO DO PEDIDO:
{order_summary}

Extraia os seguintes dados:
- nome: Nome do cliente
- telefone: Telefone sem formatação (apenas números)
- unidade: Nome da unidade/loja
- produtos: Lista de produtos com nome e preço
- endereco: Endereço completo (se for entrega)
- bairro: Nome do bairro (se for entrega)
- taxa_entrega: Valor da taxa (0 se for retirada)
- valor_total: Valor total do pedido
- forma_pagamento: Forma de pagamento
- troco: Valor do troco (se houver)
- observacoes: Observações do pedido
- tipo_entrega: "entrega" ou "retirada"

Retorne APENAS um JSON válido com a seguinte estrutura:
{{
  "nome": "string",
  "telefone": "string",
  "unidade": "string",
  "produtos": [
    {{
      "nome": "string",
      "preco": number
    }}
  ],
  "endereco": "string ou null",
  "bairro": "string ou null",
  "taxa_entrega": number,
  "valor_total": number,
  "forma_pagamento": "string",
  "troco": number ou null,
  "observacoes": "string ou null",
  "tipo_entrega": "entrega" ou "retirada"
}}
"""
