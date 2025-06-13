FROM python:3.11-slim

WORKDIR /app

COPY tracker.py .
COPY run.sh .

RUN chmod +x run.sh
RUN pip install imapclient beautifulsoup4 html2text requests

CMD ["./run.sh"]
