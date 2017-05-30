FROM python:3.6
MAINTAINER Vladimir Iakovlev <nvbn.rm@gmail.com>

COPY . /src/
RUN pip install /src

WORKDIR /data/

ENTRYPOINT ["py-backwards"]
