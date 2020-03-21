import tempfile, os

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://crispylamp:psql_pwd@localhost/postgresql'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://wtdjiseklgfzao:d5e82989a0d5f5fac66bb125ce57b131040743bdfed66b3f002a5df90d2e3017@ec2-54-159-112-44.compute-1.amazonaws.com:5432/d8k83phu8o07c2'

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    DEBUG = True
