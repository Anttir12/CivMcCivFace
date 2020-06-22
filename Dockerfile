FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV LISTEN_PORT 5000

EXPOSE 5000

COPY ./app /app
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt