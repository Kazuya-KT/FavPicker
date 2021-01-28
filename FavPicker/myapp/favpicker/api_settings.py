import os
from os.path import join, dirname
from dotenv import load_dotenv

#pwやapi_keyなどはpython_detenvで渡す

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CON_KEY = os.environ.get("CON_KEY") 
CON_SECRET = os.environ.get("CON_SECRET")