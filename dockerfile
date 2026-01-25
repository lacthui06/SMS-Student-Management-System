FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit pandas sqlalchemy mysql-connector-python openpyxl
COPY . .
EXPOSE 8501
# Sửa dòng cuối cùng trong Dockerfile thành:
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.serverAddress=localhost", "--server.headless=true"]