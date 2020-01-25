import os
import tempfile
import pytest
from pathlib import Path
import sys
from app import app, models

@pytest.fixture
def client():
    file_level_handle, TEST_DB_PATH = tempfile.mkstemp(suffix='.db',prefix='test_db')
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+ TEST_DB_PATH
    app.app.config['TESTING'] = True
    
    with app.app.test_client() as client:
        with app.app.app_context():
            app.initialize_db()
        yield client

    os.close(file_level_handle)
    os.unlink(TEST_DB_PATH)

def test_realiza_busca_no_banco_vazio(client):
	rv = client.get('/')
	assert rv.status == '200 OK'
	assert rv.data == b'{"results":[]}\n'

def test_post(client):
    object_to_create = dict(
        title='Titulo notícia',
        content='Conteudo notícia',
        site='www.xsd.com',
        date='2020-01-23 20:24',
        tick='MGLU3')
    response = client.post('/',json=object_to_create)
    assert response.status == '201 CREATED'
    # assert response.json == object_to_create