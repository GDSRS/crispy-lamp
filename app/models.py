from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class News(db.Model):
    title = db.Column(db.String(40), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(30), nullable=False)
    tick = db.Column(db.String(10), nullable=False)
    url =  db.Column(db.String(100), nullable=False, primary_key=True)
    site = db.Column(db.String(100), nullable=False, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, primary_key=True)

    def as_dict(self):
        json_object = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        json_object['date'] = self.date.strftime('%d-%m-%Y %H:%M')
        return json_object

    def to_json(self):
        return {
            'title': self.title,
            'content': self.content,
            'tick': self.tick,
            'site': self. site,
            'date': self.date.strftime('%d-%m-%Y %H:%M'),
            'author': self.author,
            'url': self.url
        }

def populate_db():#método de teste
    db.session.add(News(title='asdf', content='asdf', tick='MGLU3', site='https://site.com',
                        date=datetime.datetime.today(), author='asdf', url='asdf'))
    # db.session.add(News(title='asdf',content='asdf',tick='MGLU3',site='https://site.com',date=datetime.datetime.today() + datetime.timedelta(days=1)))
    # db.session.add(News(title='asdf',content='asdf',tick='MGLU3',site='https://site.com',date=datetime.datetime.today() + datetime.timedelta(days=2)))
    # db.session.add(News(title='asdf',content='asdf',tick='MGLU3',site='https://site.com',date=datetime.datetime.today() + datetime.timedelta(days=3)))
    # db.session.add(News(title='asdf',content='asdf',tick='MGLU3',site='https://site.com',date=datetime.datetime.today() + datetime.timedelta(days=4)))
    db.session.commit()
