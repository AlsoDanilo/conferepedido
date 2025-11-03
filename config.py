import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base da aplicação."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', False)
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4.1-mini'
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Server
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Configurações para produção."""
    DEBUG = False
    FLASK_ENV = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
