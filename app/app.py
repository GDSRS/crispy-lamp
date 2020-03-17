from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import g, Flask, request, Response, make_response # g faz parte do application context
from .models import db, News, populate_db
from app.config import DevelopmentConfig

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://crispylamp:psql_pwd@localhost/postgresql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/<string:tick>', methods=['GET'])
def get_news_by_tick(tick=None):
    if tick is not None:
        news = News.query.filter_by(tick=tick).all()
        json_result = [n.to_json() for n in news]
        return make_response({'results': json_result}, 200, {'Content-Type':'application/json'})

    return {'ERRO': 'tick deve ser especificado'}

@app.route('/', methods=['POST', 'GET'])
def post_or_get_news():
    try:
        if request.method == 'POST':
            add_news()
            return make_response({}, 201, {'Content-Type':'application/json'})
        elif request.method == 'GET':
            news = News.query.all()
            json_result = [n.to_json() for n in news]
            return make_response({'results': json_result}, 200, {'Content-Type':'application/json'})
        else:
            print('request method was', request.method)
            raise Exception
            make_response({'error': 'request method was %s' % request.method}, 500,
                          {'Content-Type': 'application/json'})
    except IntegrityError as e:
        return make_response({'error': str(e)}, 500, {'Content-Type': 'application/json'})

def add_news():
    news = News(title=request.json['title'], content=request.json['content'],
                site=request.json['site'], tick=request.json['tick'], url=request.json['url'],
                date=datetime.strptime(request.json['date'], '%d-%m-%Y %H:%M'),
                author=request.json['author'])
    db.session.add(news)
    db.session.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def initialize_db(application):
    db.init_app(application)
    with application.app_context():
        db.create_all()

if __name__ == '__main__':
    app.config.from_object(DevelopmentConfig())
    initialize_db(app)
    app.run(debug=True)
