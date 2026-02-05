#!/usr/bin/env python3
"""
Simple script to run the Flask app locally on an available port
"""

from app import create_app
from extensions import socketio
import socket

def find_free_port():
    """Find a free port to run the application"""
    ports_to_try = [5001, 5002, 5003, 5004, 5005, 8000, 8001, 8080]
    
    for port in ports_to_try:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    
    return 5000  # Default fallback

if __name__ == "__main__":
    app = create_app()
    port = find_free_port()
    
    print(f"[*] Starting InnoBridge Platform...")
    print(f"URL: http://localhost:{port}")
    print(f"Credentials:")
    print(f"   Admin: admin@test.com / admin123")
    print(f"   Startup: startup@test.com / startup123")
    print(f"   Corporate: corporate@test.com / corporate123")
    print(f"   Enabler: enabler@test.com / enabler123")
    print(f"Press Ctrl+C to stop the server")
    print(f"=" * 50)
    
    try:
        socketio.run(app, debug=True, port=port, host='0.0.0.0')
    except KeyboardInterrupt:
        print(f"\nServer stopped!")
    except Exception as e:
        print(f"Error starting server: {e}")
        print(f"Try running: python run_local.py")