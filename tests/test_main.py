# Basic test to ensure application can be imported and routes work
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route returns successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_security_verification_route(client):
    """Test that the security verification route returns successfully"""
    response = client.get('/security-verification')
    assert response.status_code == 200

def test_setup_get_route(client):
    """Test that the setup route returns successfully for GET requests"""
    response = client.get('/setup')
    assert response.status_code == 200

def test_app_creation():
    """Test that the Flask app can be created"""
    assert app is not None
    assert app.config['SECRET_KEY'] is not None
