import sqlite3
from flask import g, Flask, request, Response, make_response # g faz parte do application context
from .models import db, News, populate_db
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/<string:tick>',methods=['GET'])
def get_news_by_tick(tick=None):
    if tick is not None:
        news = News.query.filter_by(tick=tick).all()
        json_result = [n.to_json() for n in news ]
        return make_response({'results': json_result}, 200, {'Content-Type':'application/json'})
    else:
        return {'ERRO': 'tick deve ser especificado'}

@app.route('/',methods=['POST','GET'])
def post_or_get_news():
    if request.method == 'POST':
        news = News(title=request.json['title'],content=request.json['content'],site=request.json['site'],\
        date=datetime.strptime(request.json['date'],'%d-%m-%Y %H:%M'),tick=request.json['tick'])
        db.session.add(news)
        db.session.commit()
        return make_response(news.to_json(), 201, {'Content-Type':'application/json'})
    elif request.method == 'GET':
        news = News.query.all()
        json_result = [n.to_json() for n in news]
        return make_response({'results': json_result}, 200, {'Content-Type':'application/json'})
    else:
        print('request method was', request.method)
        raise Exception
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()

def pop_db():
    with app.app_context():
        initialize_db()
        if len(News.query.all()) == 0:
            populate_db()
        else:
            print("Não precisou popular")

def initialize_db():
    db.create_all()

if __name__ == '__main__':
	pop_db()
	app.run()

