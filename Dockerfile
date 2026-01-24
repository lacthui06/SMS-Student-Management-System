# 1. Base image Python
FROM python:3.10-slim

# 2. Set thư mục làm việc trong container
WORKDIR /app

# 3. Copy toàn bộ source code vào container
COPY . /app

# 4. Cài các thư viện cần thiết
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    sqlalchemy \
    mysql-connector-python

# 5. Mở port Streamlit
EXPOSE 8501

# 6. Chạy ứng dụng
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
git branch
