from app.app import app as application
from app.app import initialize_db
from app.config import ProductionConfig

application.config.from_object(ProductionConfig())
initialize_db(application)

if __name__ == '__main__':
    application.run()
