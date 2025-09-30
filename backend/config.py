"""
Configuration settings for the Flask application
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration (not needed for this simple demo)
    # DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    
    # API configuration
    CEREBRAS_API_KEY = os.environ.get('CEREBRAS_API_KEY')
    CEREBRAS_API_URL = os.environ.get('CEREBRAS_API_URL') or 'https://api.cerebras.ai/v1/chat/completions'
    
    # MCP Gateway
    MCP_GATEWAY_URL = os.environ.get('MCP_GATEWAY_URL') or 'http://mcp-gateway:3000'
