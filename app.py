"""
Aplicação Flask para validação de pedidos.
Serviço que recebe resumos de pedidos, extrai dados via LLM e valida contra banco de dados.
"""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config, config
from llm_extractor import LLMExtractor
from database import SupabaseClient, OrderValidator

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação
app = Flask(__name__)
env = Config.FLASK_ENV
app.config.from_object(config[env])

# Habilita CORS para aceitar requisições do FiqOn
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Inicializa componentes
llm_extractor = LLMExtractor()
db_client = SupabaseClient()
order_validator = OrderValidator(db_client)


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificação de saúde da aplicação.
    
    Returns:
        JSON com status da aplicação
    """
    return jsonify({
        'status': 'ok',
        'service': 'Order Validator Service',
        'version': '1.0.0'
    }), 200


@app.route('/api/validate-order', methods=['POST'])
def validate_order():
    """
    Endpoint principal para validação de pedidos.
    
    Recebe um resumo de pedido em texto, extrai dados via LLM,
    valida contra o banco de dados e retorna o resultado.
    
    Request JSON:
        {
            "resumo": "Texto do resumo do pedido..."
        }
    
    Returns:
        JSON com resultado da validação
    """
    try:
        # Valida requisição
        data = request.get_json()
        
        if not data or 'resumo' not in data:
            return jsonify({
                'erro': 'Campo "resumo" é obrigatório',
                'status': 'erro'
            }), 400
        
        resumo = data['resumo'].strip()
        
        if not resumo:
            return jsonify({
                'erro': 'Resumo não pode estar vazio',
                'status': 'erro'
            }), 400
        
        logger.info(f"Iniciando validação de pedido")
        
        # Extrai dados do resumo usando LLM
        logger.info("Etapa 1: Extração de dados com LLM")
        order_data = llm_extractor.extract_order_data(resumo)
        
        if order_data is None:
            return jsonify({
                'erro': 'Falha ao extrair dados do resumo. Verifique o formato.',
                'status': 'erro'
            }), 400
        
        # Valida dados contra banco de dados
        logger.info("Etapa 2: Validação contra banco de dados")
        validation_result = order_validator.validate_order(order_data)
        
        # Prepara resposta
        response = {
            'status': 'sucesso',
            'pedido_valido': validation_result['valido'],
            'dados_extraidos': order_data,
            'validacao': {
                'valor_total_informado': validation_result['valor_total_informado'],
                'valor_total_calculado': validation_result['valor_total_calculado'],
                'diferenca': round(
                    validation_result['valor_total_calculado'] - validation_result['valor_total_informado'],
                    2
                ),
                'erros': validation_result['erros'],
                'correcoes': validation_result['correcoes'],
                'resumo': validation_result['resumo']
            }
        }
        
        logger.info(f"Validação concluída: pedido_valido={validation_result['valido']}")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Erro ao validar pedido: {e}", exc_info=True)
        return jsonify({
            'erro': f'Erro interno do servidor: {str(e)}',
            'status': 'erro'
        }), 500


@app.route('/api/extract-order', methods=['POST'])
def extract_order():
    """
    Endpoint para apenas extrair dados do resumo (sem validação).
    Útil para debug e testes.
    
    Request JSON:
        {
            "resumo": "Texto do resumo do pedido..."
        }
    
    Returns:
        JSON com dados extraídos
    """
    try:
        data = request.get_json()
        
        if not data or 'resumo' not in data:
            return jsonify({
                'erro': 'Campo "resumo" é obrigatório',
                'status': 'erro'
            }), 400
        
        resumo = data['resumo'].strip()
        
        if not resumo:
            return jsonify({
                'erro': 'Resumo não pode estar vazio',
                'status': 'erro'
            }), 400
        
        logger.info("Extração de dados (sem validação)")
        order_data = llm_extractor.extract_order_data(resumo)
        
        if order_data is None:
            return jsonify({
                'erro': 'Falha ao extrair dados do resumo',
                'status': 'erro'
            }), 400
        
        return jsonify({
            'status': 'sucesso',
            'dados': order_data
        }), 200
    
    except Exception as e:
        logger.error(f"Erro ao extrair pedido: {e}", exc_info=True)
        return jsonify({
            'erro': f'Erro interno do servidor: {str(e)}',
            'status': 'erro'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas."""
    return jsonify({
        'erro': 'Rota não encontrada',
        'status': 'erro'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos."""
    logger.error(f"Erro interno: {error}")
    return jsonify({
        'erro': 'Erro interno do servidor',
        'status': 'erro'
    }), 500


if __name__ == '__main__':
    logger.info(f"Iniciando aplicação em modo {app.config['FLASK_ENV']}")
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
