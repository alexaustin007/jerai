import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    """Application configuration"""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Build DATABASE_URL with proper URL encoding for password
    db_user = os.getenv('MYSQL_USER', 'jerai')
    db_password = os.getenv('MYSQL_PASSWORD', 'Alex@12345')
    db_host = os.getenv('MYSQL_HOST', 'mysql')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_name = os.getenv('MYSQL_DATABASE', 'jerai')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'ssl_disabled': True
        }
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('FLASK_ENV') == 'development'

    CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
    CEREBRAS_API_URL = os.getenv('CEREBRAS_API_URL', 'https://api.cerebras.ai/v1/chat/completions')

    MCP_GATEWAY_URL = os.getenv('MCP_GATEWAY_URL', 'http://mcp-agent.railway.internal:9000')
