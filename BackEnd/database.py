# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# # Substitua por suas credenciais reais
# DB_USER = "root"
# DB_PASSWORD = ""
# DB_HOST = "localhost"
# DB_PORT = "3306"
# DB_NAME = "messager"
#
# DATABASE_URL = "sqlite:///./test.db"
#
#
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração do banco de dados (substitua pelas suas configurações)
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat_app1.db"
# Para MySQL/MariaDB:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Apenas para SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()