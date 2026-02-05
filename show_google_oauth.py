#!/usr/bin/env python3
"""
Simple server to demonstrate Google OAuth buttons
"""

from flask import Flask, render_template
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'demo-key'
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

@app.route('/')
def index():
    return '''
    <h1>🎉 Google OAuth is NOW ENABLED!</h1>
    <p><a href="/signup">View Signup Page with Google OAuth</a></p>
    <p><a href="/login">View Login Page with Google OAuth</a></p>
    <p><a href="/test">View Minimal Google Button Test</a></p>
    <p><a href="/config">Check Configuration</a></p>
    '''

@app.route('/test')
def test_page():
    with open('minimal_google_test.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/config')
def config():
    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
    
    configured = (
        client_id and 
        client_secret and 
        client_id != 'your_google_client_id_here' and 
        client_secret != 'your_google_client_secret_here'
    )
    
    return f'''
    <h2>Google OAuth Configuration Status</h2>
    <p><strong>Status:</strong> {'✅ ENABLED' if configured else '❌ DISABLED'}</p>
    <p><strong>Client ID:</strong> {client_id[:20]}... (truncated)</p>
    <p><strong>Buttons Visible:</strong> {'YES' if configured else 'NO'}</p>
    <p><a href="/">Back to Home</a></p>
    '''

@app.route('/auth/google/config-check')
def google_config_check():
    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
    
    configured = (
        client_id and 
        client_secret and 
        client_id != 'your_google_client_id_here' and 
        client_secret != 'your_google_client_secret_here'
    )
    
    return {"configured": configured}

if __name__ == '__main__':
    print("🚀 Starting Google OAuth Demo Server...")
    print("📱 Visit: http://localhost:5002")
    print("✅ Google OAuth buttons should be visible!")
    app.run(debug=True, port=5002, host='0.0.0.0')