import sqlite3
from flask import g, Flask, request, Response # g faz parte do application context
import json
from models import db, News, populate_db
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/<tick>/',methods=['GET'])
def get_news_by_tick(tick=None):
    if tick is not None:
        news = News.query.filter_by(tick=tick).all()
        json_result = [n.as_dict() for n in news ]
        print(json_result)
        return { 'results': json_result }
    else:
        return {'ERRO': 'tick deve ser especificado'}

@app.route('/',methods=['POST','GET'])
def post_or_get_news():
    if request.method == 'POST':
        news = News(title=request.json['title'],content=request.json['content'],site=request.json['site'],\
        date=datetime.strptime(request.json['date'],'%Y-%m-%d %H:%M'),tick=request.json['tick'])
        db.session.add(news)
        db.session.commit()
        #TODO: Converter para json
        return news.as_dict(), 201
    elif request.method == 'GET':
        news = News.query.all()
        json_result = [n.as_dict() for n in news]
        return {'results': json_result}
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

