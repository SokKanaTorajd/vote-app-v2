# from dotenv import load_dotenv
import os

# load_dotenv()
user = os.environ.get('user')
password = os.environ.get('password')
host= os.environ.get('host')
database = os.environ.get('database')

jwt_key = os.environ.get('jwt_key')
secret_key = os.environ.get('secret_key')

email = os.environ.get('email')
password_email = os.environ.get('password_email')