FROM sanicframework/sanic:LTS

RUN mkdir -p /srv
COPY . /srv

EXPOSE 8888

WORKDIR /srv
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "/srv/main.py"]
