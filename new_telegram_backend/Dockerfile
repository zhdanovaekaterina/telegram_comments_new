FROM python:3.10-slim AS compile-image

WORKDIR /code

COPY requirements.txt /tmp

RUN \
    pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r /tmp/requirements.txt


FROM python:3.10-slim AS build-image

RUN useradd --system zhdanova

WORKDIR /code

COPY --from=compile-image /wheels /wheels
COPY . ./src

ENV PATH=/code:$PATH
ENV PYTHONPATH /code

RUN \
    pip install --upgrade pip && \
    pip install --no-cache /wheels/*

USER zhdanova

CMD [ "python", "./src/main.py" ]
