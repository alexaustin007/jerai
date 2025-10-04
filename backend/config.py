import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    """Application configuration"""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Full URL override
    db_url = os.getenv('MYSQL_URL')

    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        db_user = os.getenv('MYSQL_USER')
        db_password = os.getenv('MYSQL_PASSWORD')
        db_host = os.getenv('MYSQL_HOST')
        db_port = os.getenv('MYSQL_PORT', '3306')
        db_name = os.getenv('MYSQL_DATABASE')

        # Optional: validate that all fields are present, or raise error early
        if not all([db_user, db_password, db_host, db_name]):
            raise RuntimeError("Missing one or more MySQL env vars (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE)")

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('FLASK_ENV') == 'development'

    CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
    CEREBRAS_API_URL = os.getenv('CEREBRAS_API_URL', 'https://api.cerebras.ai/v1/chat/completions')

    MCP_GATEWAY_URL = os.getenv('MCP_GATEWAY_URL', 'http://localhost:9000')
