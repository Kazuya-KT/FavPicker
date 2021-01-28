import os
from os.path import join, dirname
from dotenv import load_dotenv

#gitにあげられない環境変数はpython_detenvで渡す

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CON_KEY = os.environ.get("CON_KEY") 
CON_SECRET = os.environ.get("CON_SECRET")
DB_USER = os.environ.get("db_user")
DB_PASS = os.environ.get("db_pass")
SECRET_KEY = os.environ.get("SECRET_KEY")