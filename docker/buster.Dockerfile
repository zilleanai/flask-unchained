FROM debian:buster-slim
ARG VERSION=v0.7.8

ENV PYTHONUNBUFFERED 1

RUN useradd --user-group --create-home --home-dir /flask --shell /bin/false flask

RUN apt-get update && apt-get install -y build-essential python3-dev python3-pip libxml2-dev libxslt-dev libffi-dev libpq-dev git

RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s $(which pip3) pip \
	&& ln -s python3-config python-config

RUN pip install --upgrade pip && pip install --no-cache-dir -e git+https://github.com/zilleanai/flask-unchained.git#egg=flask-unchained

WORKDIR /flask/src

USER flask

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
EXPOSE 5000
