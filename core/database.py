# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Cấu hình URL (Thay đổi pass nếu cần)
DB_URL = 'mysql+mysqlconnector://root:221106@localhost/gr2'

# 2. Tạo Engine
engine = create_engine(DB_URL, pool_recycle=3600, echo=False)

# 3. Tạo Session Factory
Session = sessionmaker(bind=engine)

# 4. Tạo Base (Dùng chung cho các Models kế thừa)
Base = declarative_base()