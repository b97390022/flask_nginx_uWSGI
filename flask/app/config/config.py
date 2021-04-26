import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))


def create_sqlite_uri(db_name):
    return "sqlite:///" + os.path.join(basedir, db_name)


class BaseConfig:  # 基本配置
    SECRET_KEY = b'\xdd\x88w\x1a\x08;\xcaj\x99\xee|\xbbN\ns\xbe\xc8Z\x18\xa5nV2\xf4'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(seconds=5)

    JWT_SECRET_KEY = b'\xdd\x88w\x1a\x08;\xcaj\x99\xee|\xbbN\ns\xbe\xc8Z\x18\xa5nV2\xf4'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)


class DevelopmentConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:brucechen@db:3306/flask_nginx_uWSGI'

    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_DEFAULT_SENDER=('flask_nginx_uWSGI', 'r01442018@g.ntu.edu.tw')
    MAIL_MAX_EMAILS=10
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = create_sqlite_uri("test.db")
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
    'base': BaseConfig
}