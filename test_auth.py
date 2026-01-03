"""
Minimal Flask app to test if auth blueprint works
"""
from flask import Flask, request
from auth import bp as auth_bp
from extensions import db, login_manager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Register auth blueprint
app.register_blueprint(auth_bp)

print("=" * 80)
print("TESTING AUTH BLUEPRINT")
print("=" * 80)
print()

with app.app_context():
    # List all routes
    for rule in app.url_map.iter_rules():
        if 'auth' in str(rule) or 'login' in str(rule):
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{str(rule):30} Methods: {methods:15} → {rule.endpoint}")

print()
print("=" * 80)
print("\nStarting test server on http://localhost:5001")
print("Try: curl -X POST http://localhost:5001/auth/login -d 'email=admin@test.com&password=admin123'")
print("=" * 80)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
