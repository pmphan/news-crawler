FROM python:3.10-alpine AS crawler-py

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["scrapy", "crawl"]
