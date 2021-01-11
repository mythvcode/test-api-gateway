FROM python:3.8

WORKDIR /opt/api-gateway

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8035 --workers=3"
ENV INDOCKER=true
ENV KEYSTONE_URL="http://localhost/identity"
EXPOSE 8035/tcp

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY wsgi.py ./
ADD appmods ./appmods
RUN mkdir -p /var/log/api-gateway

RUN groupadd --gid 1000 api \
  && useradd --uid 1000  --gid api api
RUN chown api:api /var/log/api-gateway
USER api
CMD ["gunicorn", "wsgi:app"]
