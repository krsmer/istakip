# Vercel serverless function entry point
import os
import sys

# Ana dizini Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app import app
    
    # Vercel için handler
    def handler(request, response):
        return app(request, response)
    
    # WSGI compatible
    application = app
    
except Exception as e:
    print(f"Import error: {e}")
    # Fallback basit Flask app
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({"error": "Import failed", "message": str(e)})
    
    @app.route('/health')  
    def health():
        return jsonify({"status": "error", "message": "Import failed"})
    
    application = app

if __name__ == "__main__":
    app.run(debug=True)
