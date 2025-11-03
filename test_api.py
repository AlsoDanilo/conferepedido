"""
Script de testes para validação da API de pedidos.
Executa testes com exemplos reais de resumos.
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuração
API_URL = "http://localhost:5000"
ENDPOINTS = {
    'health': f"{API_URL}/health",
    'validate': f"{API_URL}/api/validate-order",
    'extract': f"{API_URL}/api/extract-order"
}

# Exemplos de resumos para teste
RESUMO_VALIDO = """Perfeito! Aqui está o RESUMO
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
OBSERVAÇÕES: Sem cebola na pizza pequena"""

RESUMO_COM_ERRO_PRECO = """Perfeito! Aqui está o RESUMO
NOME: Maria Santos
TELEFONE: (62) 98888-7777
UNIDADE: Maria Dilce
PRODUTOS SOLICITADOS: 1 Pizza grande Calabresa Acebolada - R$ 55,00
1 Pizza pequena Mussarela - R$ 27,00
ENDEREÇO: Rua das Flores, Qd 12 Lt 5, Vila Cristina
TAXA DE ENTREGA: R$ 3,00
VALOR TOTAL: R$ 85,00
FORMA DE PAGAMENTO: Dinheiro
OBSERVAÇÕES: Nenhuma"""

RESUMO_RETIRADA = """Perfeito! Aqui está o RESUMO
NOME: Carlos Oliveira
TELEFONE: (62) 97777-6666
UNIDADE: Maria Dilce
PRODUTOS SOLICITADOS: 2 Pizza grande Calabresa Acebolada - R$ 100,00
RETIRADA NA LOJA
VALOR TOTAL: R$ 100,00
FORMA DE PAGAMENTO: Cartão
OBSERVAÇÕES: Sem observação"""


def print_header(text: str):
    """Imprime um cabeçalho formatado."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_result(title: str, status: str, data: Dict[str, Any]):
    """Imprime resultado de um teste."""
    status_symbol = "✓" if status == "SUCESSO" else "✗"
    print(f"{status_symbol} {title}")
    print(f"  Status: {status}")
    print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)}\n")


def test_health_check():
    """Testa o endpoint de health check."""
    print_header("TESTE 1: Health Check")
    
    try:
        response = requests.get(ENDPOINTS['health'], timeout=5)
        
        if response.status_code == 200:
            print_result(
                "Health Check",
                "SUCESSO",
                response.json()
            )
            return True
        else:
            print_result(
                "Health Check",
                "ERRO",
                {"status_code": response.status_code, "message": response.text}
            )
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ Erro: Não foi possível conectar ao servidor")
        print("  Certifique-se de que a aplicação está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False


def test_extract_order():
    """Testa o endpoint de extração de dados."""
    print_header("TESTE 2: Extração de Dados (sem validação)")
    
    try:
        payload = {"resumo": RESUMO_VALIDO}
        response = requests.post(ENDPOINTS['extract'], json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(
                "Extração de Dados",
                "SUCESSO",
                data
            )
            return True
        else:
            print_result(
                "Extração de Dados",
                "ERRO",
                {"status_code": response.status_code, "message": response.text}
            )
            return False
    
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False


def test_validate_order_valid():
    """Testa validação de pedido válido."""
    print_header("TESTE 3: Validação de Pedido Válido")
    
    try:
        payload = {"resumo": RESUMO_VALIDO}
        response = requests.post(ENDPOINTS['validate'], json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('pedido_valido'):
                print_result(
                    "Validação - Pedido Válido",
                    "SUCESSO",
                    data
                )
                return True
            else:
                print_result(
                    "Validação - Pedido Válido",
                    "ERRO (Pedido marcado como inválido)",
                    data
                )
                return False
        else:
            print_result(
                "Validação - Pedido Válido",
                "ERRO",
                {"status_code": response.status_code, "message": response.text}
            )
            return False
    
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False


def test_validate_order_with_error():
    """Testa validação de pedido com erro de preço."""
    print_header("TESTE 4: Validação de Pedido com Erro")
    
    try:
        payload = {"resumo": RESUMO_COM_ERRO_PRECO}
        response = requests.post(ENDPOINTS['validate'], json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data.get('pedido_valido'):
                print_result(
                    "Validação - Pedido com Erro",
                    "SUCESSO (Erro detectado corretamente)",
                    data
                )
                return True
            else:
                print_result(
                    "Validação - Pedido com Erro",
                    "ERRO (Erro não foi detectado)",
                    data
                )
                return False
        else:
            print_result(
                "Validação - Pedido com Erro",
                "ERRO",
                {"status_code": response.status_code, "message": response.text}
            )
            return False
    
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False


def test_validate_order_retirada():
    """Testa validação de pedido com retirada na loja."""
    print_header("TESTE 5: Validação de Pedido com Retirada")
    
    try:
        payload = {"resumo": RESUMO_RETIRADA}
        response = requests.post(ENDPOINTS['validate'], json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verifica se taxa de entrega é 0
            if data.get('dados_extraidos', {}).get('tipo_entrega') == 'retirada':
                print_result(
                    "Validação - Retirada na Loja",
                    "SUCESSO",
                    data
                )
                return True
            else:
                print_result(
                    "Validação - Retirada na Loja",
                    "ERRO (Tipo de entrega não identificado)",
                    data
                )
                return False
        else:
            print_result(
                "Validação - Retirada na Loja",
                "ERRO",
                {"status_code": response.status_code, "message": response.text}
            )
            return False
    
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False


def test_invalid_request():
    """Testa requisição inválida."""
    print_header("TESTE 6: Requisição Inválida")
    
    try:
        payload = {}  # Sem campo 'resumo'
        response = requests.post(ENDPOINTS['validate'], json=payload, timeout=5)
        
        if response.status_code == 400:
            print_result(
                "Requisição Inválida",
                "SUCESSO (Erro 400 retornado corretamente)",
                response.json()
            )
            return True
        else:
            print_result(
                "Requisição Inválida",
                "ERRO (Status code inesperado)",
                {"status_code": response.status_code}
            )
            return False
    
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False


def run_all_tests():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "TESTES DA API DE VALIDAÇÃO DE PEDIDOS" + " "*15 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Health Check", test_health_check),
        ("Extração de Dados", test_extract_order),
        ("Pedido Válido", test_validate_order_valid),
        ("Pedido com Erro", test_validate_order_with_error),
        ("Retirada na Loja", test_validate_order_retirada),
        ("Requisição Inválida", test_invalid_request),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Erro ao executar teste '{test_name}': {str(e)}")
            results[test_name] = False
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total de testes: {total}")
    print(f"✓ Passou: {passed}")
    print(f"✗ Falhou: {failed}")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%\n")
    
    for test_name, result in results.items():
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}")
    
    print()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
