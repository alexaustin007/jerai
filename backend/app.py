"""
Jerai - Minimal AI-assisted bug fixing system
Flask backend with issue tracker and e-commerce demo
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models.base import init_db

# Import blueprints
from routes.issues import issues_bp
from routes.shop import shop_bp


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend with explicit method support
    CORS(app,
         resources={r"/api/*": {"origins": "*"}},
         methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(issues_bp, url_prefix='/api/issues')
    app.register_blueprint(shop_bp, url_prefix='/api/shop')

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "jerai-backend"})

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            "service": "Jerai API",
            "endpoints": {
                "issues": "/api/issues",
                "shop": "/api/shop",
                "health": "/health"
            }
        })

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)