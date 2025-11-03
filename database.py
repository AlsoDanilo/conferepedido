"""
Módulo para integração com Supabase e validação de dados contra o banco.
"""

import logging
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client
from config import Config

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Cliente para integração com Supabase."""
    
    def __init__(self):
        """Inicializa o cliente Supabase."""
        try:
            self.client: Client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
            logger.info("Conectado ao Supabase com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Supabase: {e}")
            self.client = None
    
    def get_product_by_name_and_size(self, nome: str, tamanho: str) -> Optional[Dict]:
        """
        Busca um produto pelo nome e tamanho.
        
        Args:
            nome: Nome do produto
            tamanho: Tamanho (grande, pequeno, médio)
            
        Returns:
            Dicionário com dados do produto ou None
        """
        try:
            response = self.client.table('produtos').select('*').eq('status', 'Disponível').execute()
            
            for produto in response.data:
                if self._normalize_text(produto['nome']) == self._normalize_text(nome) and \
                   self._normalize_text(produto['tamanho']) == self._normalize_text(tamanho):
                    return produto
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {e}")
            return None
    
    def get_neighborhood_tax(self, bairro: str) -> Optional[Dict]:
        """
        Busca a taxa de entrega para um bairro.
        
        Args:
            bairro: Nome do bairro
            
        Returns:
            Dicionário com dados do bairro ou None
        """
        try:
            response = self.client.table('bairros').select('*').eq('status', 'Disponível').execute()
            
            for neighborhood in response.data:
                if self._normalize_text(neighborhood['nome']) == self._normalize_text(bairro):
                    return neighborhood
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar bairro: {e}")
            return None
    
    def get_additional_by_name_and_size(self, nome: str, tamanho: str = None) -> Optional[Dict]:
        """
        Busca um adicional pelo nome e tamanho (opcional).
        
        Args:
            nome: Nome do adicional
            tamanho: Tamanho (opcional)
            
        Returns:
            Dicionário com dados do adicional ou None
        """
        try:
            response = self.client.table('adicionais').select('*').eq('status', 'Disponível').execute()
            
            for adicional in response.data:
                if self._normalize_text(adicional['nome']) == self._normalize_text(nome):
                    if tamanho is None or self._normalize_text(adicional.get('tamanho', '')) == self._normalize_text(tamanho):
                        return adicional
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar adicional: {e}")
            return None
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normaliza texto para comparação (minúsculas, sem acentos).
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        import unicodedata
        
        if not text:
            return ""
        
        # Remove acentos
        text = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        
        # Converte para minúsculas
        return text.lower().strip()


class OrderValidator:
    """Valida dados de pedidos contra o banco de dados."""
    
    def __init__(self, db_client: SupabaseClient):
        """
        Inicializa o validador.
        
        Args:
            db_client: Cliente Supabase
        """
        self.db = db_client
    
    def validate_order(self, order_data: Dict) -> Dict:
        """
        Valida um pedido completo.
        
        Args:
            order_data: Dados do pedido extraídos
            
        Returns:
            Dicionário com resultado da validação
        """
        errors = []
        corrections = []
        calculated_total = 0
        
        # Valida produtos
        products_validation = self._validate_products(order_data.get('produtos', []))
        errors.extend(products_validation['errors'])
        corrections.extend(products_validation['corrections'])
        calculated_total += products_validation['subtotal']
        
        # Valida taxa de entrega
        if order_data.get('tipo_entrega') == 'entrega':
            tax_validation = self._validate_delivery_tax(
                order_data.get('bairro'),
                order_data.get('taxa_entrega')
            )
            errors.extend(tax_validation['errors'])
            corrections.extend(tax_validation['corrections'])
            calculated_total += tax_validation['tax_amount']
        
        # Valida valor total
        total_validation = self._validate_total(
            order_data.get('valor_total'),
            calculated_total
        )
        errors.extend(total_validation['errors'])
        corrections.extend(total_validation['corrections'])
        
        # Prepara resposta
        is_valid = len(errors) == 0
        
        return {
            'valido': is_valid,
            'valor_total_calculado': calculated_total,
            'valor_total_informado': order_data.get('valor_total'),
            'erros': errors,
            'correcoes': corrections,
            'resumo': self._build_summary(is_valid, errors, corrections)
        }
    
    def _validate_products(self, products: List[Dict]) -> Dict:
        """
        Valida produtos do pedido.
        
        Args:
            products: Lista de produtos
            
        Returns:
            Dicionário com resultado da validação
        """
        errors = []
        corrections = []
        subtotal = 0
        
        for product in products:
            nome = product.get('nome', '')
            preco_informado = product.get('preco', 0)
            
            # Tenta extrair tamanho do nome
            tamanho = self._extract_size_from_name(nome)
            
            # Busca produto no banco
            db_product = self.db.get_product_by_name_and_size(nome, tamanho)
            
            if db_product is None:
                errors.append(f"Produto '{nome}' não encontrado no cardápio")
            else:
                preco_correto = float(db_product['preco'])
                
                if abs(preco_informado - preco_correto) > 0.01:
                    errors.append(
                        f"Preço incorreto para '{nome}': "
                        f"informado R$ {preco_informado:.2f}, "
                        f"correto R$ {preco_correto:.2f}"
                    )
                    corrections.append({
                        'produto': nome,
                        'preco_informado': preco_informado,
                        'preco_correto': preco_correto,
                        'diferenca': preco_correto - preco_informado
                    })
                    subtotal += preco_correto
                else:
                    subtotal += preco_informado
        
        return {
            'errors': errors,
            'corrections': corrections,
            'subtotal': subtotal
        }
    
    def _validate_delivery_tax(self, bairro: str, taxa_informada: float) -> Dict:
        """
        Valida taxa de entrega.
        
        Args:
            bairro: Nome do bairro
            taxa_informada: Taxa informada no pedido
            
        Returns:
            Dicionário com resultado da validação
        """
        errors = []
        corrections = []
        tax_amount = 0
        
        if not bairro:
            errors.append("Bairro não informado para entrega")
            return {'errors': errors, 'corrections': corrections, 'tax_amount': 0}
        
        db_neighborhood = self.db.get_neighborhood_tax(bairro)
        
        if db_neighborhood is None:
            errors.append(f"Bairro '{bairro}' não encontrado ou indisponível")
        else:
            taxa_correta = float(db_neighborhood['taxa'])
            
            if abs(taxa_informada - taxa_correta) > 0.01:
                errors.append(
                    f"Taxa de entrega incorreta para '{bairro}': "
                    f"informada R$ {taxa_informada:.2f}, "
                    f"correta R$ {taxa_correta:.2f}"
                )
                corrections.append({
                    'bairro': bairro,
                    'taxa_informada': taxa_informada,
                    'taxa_correta': taxa_correta,
                    'diferenca': taxa_correta - taxa_informada
                })
                tax_amount = taxa_correta
            else:
                tax_amount = taxa_informada
        
        return {
            'errors': errors,
            'corrections': corrections,
            'tax_amount': tax_amount
        }
    
    def _validate_total(self, valor_total_informado: float, valor_total_calculado: float) -> Dict:
        """
        Valida valor total do pedido.
        
        Args:
            valor_total_informado: Valor total informado
            valor_total_calculado: Valor total calculado
            
        Returns:
            Dicionário com resultado da validação
        """
        errors = []
        corrections = []
        
        if abs(valor_total_informado - valor_total_calculado) > 0.01:
            errors.append(
                f"Valor total incorreto: "
                f"informado R$ {valor_total_informado:.2f}, "
                f"calculado R$ {valor_total_calculado:.2f}"
            )
            corrections.append({
                'valor_informado': valor_total_informado,
                'valor_calculado': valor_total_calculado,
                'diferenca': valor_total_calculado - valor_total_informado
            })
        
        return {
            'errors': errors,
            'corrections': corrections
        }
    
    @staticmethod
    def _extract_size_from_name(nome: str) -> str:
        """
        Extrai tamanho do nome do produto.
        
        Args:
            nome: Nome do produto
            
        Returns:
            Tamanho extraído ou string vazia
        """
        nome_lower = nome.lower()
        
        if 'grande' in nome_lower:
            return 'grande'
        elif 'pequena' in nome_lower or 'pequeno' in nome_lower:
            return 'pequeno'
        elif 'média' in nome_lower or 'médio' in nome_lower:
            return 'médio'
        
        return ''
    
    @staticmethod
    def _build_summary(is_valid: bool, errors: List[str], corrections: List[Dict]) -> str:
        """
        Constrói um resumo legível da validação.
        
        Args:
            is_valid: Se o pedido é válido
            errors: Lista de erros
            corrections: Lista de correções
            
        Returns:
            Resumo formatado
        """
        if is_valid:
            return "✓ Pedido validado com sucesso! Todos os valores estão corretos."
        
        summary = "✗ Pedido contém erros:\n\n"
        
        for i, error in enumerate(errors, 1):
            summary += f"{i}. {error}\n"
        
        if corrections:
            summary += "\nCorreções necessárias:\n"
            for correction in corrections:
                if 'preco_correto' in correction:
                    summary += f"- {correction['produto']}: R$ {correction['preco_correto']:.2f}\n"
                elif 'taxa_correta' in correction:
                    summary += f"- Taxa para {correction['bairro']}: R$ {correction['taxa_correta']:.2f}\n"
                elif 'valor_calculado' in correction:
                    summary += f"- Valor total correto: R$ {correction['valor_calculado']:.2f}\n"
        
        return summary
