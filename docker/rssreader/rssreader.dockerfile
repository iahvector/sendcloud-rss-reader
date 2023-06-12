FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN groupadd --gid 1000 worker \
    && useradd --uid 1000 --gid 1000 -m worker
USER worker:worker

COPY --chown=worker:worker ./rssreader /app
WORKDIR /app

RUN pip install -r /app/requirements.txt
ENV PATH=$PATH:/home/worker/.local/bin

RUN mkdir -p /app/static
RUN python ./manage.py collectstatic --noinput

EXPOSE 8000
CMD gunicorn --bind=0.0.0.0:8000 rssreader.wsgi