import os
import tempfile
import pytest
from app import app, models
from sqlite3 import IntegrityError


json_object = dict(
        title='Titulo notícia',
        content='Conteudo notícia',
        site='www.xsd.com',
        date='23-01-2020 20:24',
        tick='MGLU3')

@pytest.fixture(scope='function')
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

def test_empty_db(client):
	rv = client.get('/')
	assert rv.status == '200 OK'
	assert rv.data == b'{"results":[]}\n'

def test_post(client):
    response = client.post('/',json=json_object)
    assert response.status == '201 CREATED'
    assert response.json == json_object

def test_get_one_news(client):
    client.post('/',json=json_object)
    response = client.get('/'+json_object['tick'])
    assert len(response.json['results']) == 1
    assert response.json['results'][0] == json_object

def test_save_same_object(client):
    with pytest.raises(Exception) as e:
        client.post('/',json=json_object)
        client.post('/',json=json_object)
    assert e.typename == 'IntegrityError'
    assert str(e.value.orig) == 'UNIQUE constraint failed: news.site, news.date'
