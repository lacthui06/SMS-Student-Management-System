# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

db_host = os.getenv('DB_HOST', 'localhost')

# Ghép vào chuỗi kết nối (Dùng f-string)
DB_URL = f'mysql+mysqlconnector://root:221106@{db_host}/gr2'

# 2. Tạo Engine
engine = create_engine(DB_URL, pool_recycle=3600, echo=False)

# 3. Tạo Session Factory
Session = sessionmaker(bind=engine)

# 4. Tạo Base (Dùng chung cho các Models kế thừa)
Base = declarative_base()