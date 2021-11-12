FROM python:3.6

RUN pip install psycopg2-binary sqlalchemy web3 PyPubSub tronapi pika pyyaml python-dotenv uvicorn fastapi pydantic

WORKDIR /app
COPY . /app

CMD ["python", "./main.py"]

EXPOSE 8888
EXPOSE 8000