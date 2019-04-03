FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app .
CMD ["python", "server.py"]
