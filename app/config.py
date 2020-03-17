import tempfile, os

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://crispylamp:psql_pwd@localhost/postgresql'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://clozuwufxmwuhx:7b53d49d62307c04659ea632443e3fc4a25e60e8ab9f0964c3750e47bc327928@ec2-18-210-51-239.compute-1.amazonaws.com:5432/d4h51f9ilflm6r'

class DevelopmentConfig(Config):
    DEBUG = True

    