-- ============================================================================
-- Script SQL para criar as tabelas no Supabase
-- Execute este script no SQL Editor do Supabase
-- ============================================================================

-- Tabela: bairros
-- Armazena os bairros de entrega com seus respectivos preços de taxa
CREATE TABLE IF NOT EXISTS bairros (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL UNIQUE,
  taxa NUMERIC(10, 2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Disponível' CHECK (status IN ('Disponível', 'Indisponível')),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca rápida por nome
CREATE INDEX IF NOT EXISTS idx_bairros_nome ON bairros(nome);
CREATE INDEX IF NOT EXISTS idx_bairros_status ON bairros(status);

-- Tabela: adicionais
-- Guarda os adicionais que podem ser pedidos com pizzas, bordas etc.
CREATE TABLE IF NOT EXISTS adicionais (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  tipo VARCHAR(50) NOT NULL,
  tamanho VARCHAR(50),
  preco NUMERIC(10, 2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Disponível' CHECK (status IN ('Disponível', 'Indisponível')),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para buscas rápidas
CREATE INDEX IF NOT EXISTS idx_adicionais_nome ON adicionais(nome);
CREATE INDEX IF NOT EXISTS idx_adicionais_tipo ON adicionais(tipo);
CREATE INDEX IF NOT EXISTS idx_adicionais_status ON adicionais(status);

-- Tabela: produtos
-- Contém os produtos do cardápio, incluindo pizzas, pizzaburgers e bebidas
CREATE TABLE IF NOT EXISTS produtos (
  id SERIAL PRIMARY KEY,
  tipo VARCHAR(50) NOT NULL,
  nome VARCHAR(255) NOT NULL,
  ingredientes TEXT,
  tamanho VARCHAR(50) NOT NULL,
  preco NUMERIC(10, 2) NOT NULL,
  status VARCHAR(20) DEFAULT 'Disponível' CHECK (status IN ('Disponível', 'Indisponível')),
  categoria VARCHAR(100),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para buscas rápidas
CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome);
CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo);
CREATE INDEX IF NOT EXISTS idx_produtos_tamanho ON produtos(tamanho);
CREATE INDEX IF NOT EXISTS idx_produtos_status ON produtos(status);
CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);

-- ============================================================================
-- DADOS DE EXEMPLO PARA TESTES
-- ============================================================================

-- Inserir bairros de exemplo
INSERT INTO bairros (nome, taxa, status) VALUES
  ('Vila Cristina', 3.00, 'Disponível'),
  ('Centro', 2.50, 'Disponível'),
  ('Setor Leste', 4.00, 'Disponível'),
  ('Setor Oeste', 3.50, 'Disponível'),
  ('Zona Rural', 5.00, 'Disponível')
ON CONFLICT (nome) DO NOTHING;

-- Inserir produtos de exemplo (Pizzas)
INSERT INTO produtos (tipo, nome, ingredientes, tamanho, preco, status, categoria) VALUES
  ('pizza', 'Pizza Calabresa Acebolada', 'Calabresa, cebola, molho de tomate, queijo', 'grande', 50.00, 'Disponível', 'pizza tradicional'),
  ('pizza', 'Pizza Calabresa Acebolada', 'Calabresa, cebola, molho de tomate, queijo', 'pequeno', 30.00, 'Disponível', 'pizza tradicional'),
  ('pizza', 'Pizza Mussarela', 'Queijo mussarela, molho de tomate', 'grande', 45.00, 'Disponível', 'pizza tradicional'),
  ('pizza', 'Pizza Mussarela', 'Queijo mussarela, molho de tomate', 'pequeno', 27.00, 'Disponível', 'pizza tradicional'),
  ('pizza', 'Pizza Brigadeiro', 'Brigadeiro, chocolate, granulado', 'grande', 48.00, 'Disponível', 'pizza doce'),
  ('pizza', 'Pizza Brigadeiro', 'Brigadeiro, chocolate, granulado', 'pequeno', 28.00, 'Disponível', 'pizza doce'),
  ('pizza', 'Pizza Frango com Catupiry', 'Frango desfiado, catupiry, molho de tomate', 'grande', 52.00, 'Disponível', 'pizza premium'),
  ('pizza', 'Pizza Frango com Catupiry', 'Frango desfiado, catupiry, molho de tomate', 'pequeno', 32.00, 'Disponível', 'pizza premium'),
  ('pizza', 'Pizza Vegetariana', 'Brócolis, cenoura, milho, cebola, pimentão', 'grande', 42.00, 'Disponível', 'pizza vegetariana'),
  ('pizza', 'Pizza Vegetariana', 'Brócolis, cenoura, milho, cebola, pimentão', 'pequeno', 25.00, 'Disponível', 'pizza vegetariana')
ON CONFLICT DO NOTHING;

-- Inserir adicionais de exemplo
INSERT INTO adicionais (nome, tipo, tamanho, preco, status) VALUES
  ('Borda de Queijo', 'borda', 'grande', 5.00, 'Disponível'),
  ('Borda de Queijo', 'borda', 'pequeno', 3.00, 'Disponível'),
  ('Borda Recheada', 'borda', 'grande', 8.00, 'Disponível'),
  ('Borda Recheada', 'borda', 'pequeno', 5.00, 'Disponível'),
  ('Refrigerante 2L', 'bebida', NULL, 8.00, 'Disponível'),
  ('Refrigerante Lata', 'bebida', NULL, 3.50, 'Disponível'),
  ('Suco Natural', 'bebida', NULL, 6.00, 'Disponível'),
  ('Agua', 'bebida', NULL, 2.00, 'Disponível')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICAÇÃO
-- ============================================================================

-- Contar registros em cada tabela
SELECT 'bairros' as tabela, COUNT(*) as total FROM bairros
UNION ALL
SELECT 'produtos' as tabela, COUNT(*) as total FROM produtos
UNION ALL
SELECT 'adicionais' as tabela, COUNT(*) as total FROM adicionais;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================
-- 1. Substitua os dados de exemplo pelos seus dados reais
-- 2. Certifique-se de que os nomes dos produtos correspondem aos que o bot extrai
-- 3. Mantenha a normalização de nomes (minúsculas, sem acentos) para melhor matching
-- 4. Atualize os preços conforme necessário
-- 5. Use status 'Disponível' ou 'Indisponível' para controlar disponibilidade
