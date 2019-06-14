FROM alpine:latest

RUN apt-get update -y && apt-get install -y python python-pip python-dev build-essential

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]


