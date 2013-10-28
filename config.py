import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

GCM_API_KEY = "AIzaSyCjL0IFxGGz_cn-_t_iyu0AwnCltQY_3JE"