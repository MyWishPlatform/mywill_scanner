FROM python:3.6

WORKDIR /app
COPY . /app

RUN pip install psycopg2-binary sqlalchemy web3 PyPubSub tronapi pika pyyaml python-dotenv uvicorn fastapi pydantic


CMD ["python", "main.py"]
EXPOSE 8888