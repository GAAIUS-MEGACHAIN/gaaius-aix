#!/usr/bin/env python
"""Start the GAAIUS AI Builder server."""
import os
import subprocess
import sys

# Set environment variables
os.environ['GROQ_API_KEY'] = os.environ.get('GROQ_API_KEY', 'test-key')
os.environ['MONGO_URL'] = os.environ.get('MONGO_URL', 'mongodb://127.0.0.1:27017')
os.environ['DB_NAME'] = os.environ.get('DB_NAME', 'gaaius')
os.environ['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')

print("🚀 Starting GAAIUS AI Builder Server...")
print(f"   GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT SET')[:10]}...")
print(f"   MONGO_URL: {os.environ.get('MONGO_URL')}")
print(f"   DB_NAME: {os.environ.get('DB_NAME')}")
print(f"   Server will be available at: http://127.0.0.1:8000")
print()

# Start the server
try:
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'backend.server:app',
        '--host', '127.0.0.1',
        '--port', '8000',
        '--log-level', 'info'
    ])
except KeyboardInterrupt:
    print("\n✋ Server stopped")
    sys.exit(0)
