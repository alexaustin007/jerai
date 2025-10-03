import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Config:
    """Application configuration"""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Build DATABASE_URL with proper URL encoding for password
    db_user = os.getenv('MYSQL_USER', 'root')
    db_password = os.getenv('MYSQL_PASSWORD', 'Password@77')
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_name = os.getenv('MYSQL_DATABASE', 'jerai')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:3306/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('FLASK_ENV') == 'development'

    CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
    CEREBRAS_API_URL = os.getenv('CEREBRAS_API_URL', 'https://api.cerebras.ai/v1/chat/completions')

    MCP_GATEWAY_URL = os.getenv('MCP_GATEWAY_URL', 'http://localhost:3000')
