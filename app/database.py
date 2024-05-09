from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-address/hostname>/<database_name>'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  THIS IS FOR REGULAR CONNECTION USING POSTGRES DRIVER.

# from datetime import time

# from psycopg2.extras import RealDictCursor
# from sqlalchemy.dialects.postgresql import psycopg2

# while True:
#     try:
#         conn = psycopg2.connect(host='127.0.0.1', database='fastapi_db', user='postgres',
#                                 password='36975306', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Connection failed")
#         print(error)
#         time.sleep(2)
