FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
# Le CMD peut être override dans docker-compose.yml
CMD ["python", "train_model.py"]
