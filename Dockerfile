FROM python:3.9-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY classes/ .
COPY modules/ .
COPY src/ .

CMD [ "python", "./bot_main.py" ]
