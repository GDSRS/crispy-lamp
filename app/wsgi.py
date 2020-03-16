from app.app import app as application
from app.app import pop_db

if __name__ == '__main__':
    pop_db()
    application.run()
