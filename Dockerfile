FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip uv \
    && uv pip install -r requirements.txt \
    && uv pip install pymysql minio
CMD ["python", "extraction_creation_sql.py"]
