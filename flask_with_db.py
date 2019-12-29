import sqlite3
from flask import g, Flask, request # g faz parte do application context

app = Flask(__name__)

DATABASE = './database.db'


def get_db():
    db = getattr(g, '_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/',methods=['POST'])
@app.route('/<news_id>/',methods=['GET'])
def post_or_get(news_id=None):
    if request.method == 'POST':
        print(request.json)
        query = 'INSERT INTO NEWS (title, content, site, data) VALUES(?,?,?,?)'
        tuple_element = (request.json['title'],request.json['content'],request.json['site'],request.json['data'])
        return str(query_db(query,tuple_element))
    elif request.method == 'GET': 
        query = 'SELECT rowid, * FROM NEWS WHERE rowid = ?'
        _id, title, content, tick, site, data = query_db(query,[news_id],one=True)
        print(query_db(query,[news_id],one=True))
        return {'id':_id, 'title': title, 'content': content,'tick': tick, 'site': site, 'data': data}
    else:
        raise Exception

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()

def query_db(query, args=(),one=False):
    db = get_db()
    cur = db.execute(query,args)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()
app.run()

