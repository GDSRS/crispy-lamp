import os, tempfile
import pytest
from app.app import app, initialize_db
from app.models import db

json_object = dict(
        title='Titulo notícia',
        content='Conteudo notícia',
        site='www.xsd.com',
        date='23-01-2020 20:24',
        tick='MGLU3',
        url='url',
        author='junin autor')




@pytest.fixture(scope='function')
def client():
    file_level_handle, TEST_DB_PATH = tempfile.mkstemp(suffix='.db',prefix='test_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ TEST_DB_PATH

    db.init_app(app)

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(file_level_handle)
    print('TEST DB PATH', TEST_DB_PATH)
    os.unlink(TEST_DB_PATH)

def test_empty_db(client):
	rv = client.get('/')
	assert rv.status == '200 OK'
	assert rv.data == b'{"results":[]}\n'

def test_post(client):
    response = client.post('/',json=json_object)
    assert response.status == '201 CREATED'
    # assert response.json == json_object

def test_get_one_news(client):
    client.post('/',json=json_object)
    response = client.get('/tick/'+json_object['tick'])
    assert len(response.json['results']) == 1
    assert response.json['results'][0] == json_object

def test_erro_save_same_object(client):
    response = client.post('/',json=json_object)
    response.status_code == 200
    response = client.post('/',json=json_object)
    assert response.status_code == 500
    assert 'UNIQUE constraint failed' in response.json['error']
