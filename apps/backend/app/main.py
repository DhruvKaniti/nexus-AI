from flask import Flask, jsonify, request
from flask_cors import CORS
from app.api import investigate, global_scan
import logging
import re

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://nexus-ai-gamma-drab.vercel.app",
            "http://localhost:5173",
            "http://localhost:3000"
        ]
    }
})# Register routes with /api prefix
app.register_blueprint(investigate.bp, url_prefix='/api')
app.register_blueprint(global_scan.bp, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({"status": "Nexus AI backend running"})

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

# Global error handler - ensure ALL responses are JSON
@app.errorhandler(Exception)
def handle_exception(e):
    """Catch all unhandled exceptions and return JSON"""
    logging.getLogger(__name__).error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({
        "error": str(e),
        "error_type": type(e).__name__,
        "api_version": "2.1"
    }), 500



@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "api_version": "2.1"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": str(e) if str(e) else "Internal server error",
        "api_version": "2.1"
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
