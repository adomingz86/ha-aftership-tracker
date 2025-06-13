FROM python:3.11-slim

WORKDIR /app

COPY tracker.py .

RUN pip install imapclient beautifulsoup4 html2text requests

CMD ["python", "tracker.py"]