FROM python:3.7-alpine
ADD ./app /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
