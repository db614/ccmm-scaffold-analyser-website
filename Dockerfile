FROM python:3.6

RUN adduser --gecos --disabled-password ccmmdb

WORKDIR /home/ccmmdb

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN pip3 --no-cache-dir install -r requirements.txt
RUN pip3 install gunicorn

COPY ccmmdb ccmmdb
COPY boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP /home/ccmmdb/ccmmdb/__init__.py

RUN chown -R ccmmdb:ccmmdb ./
USER ccmmdb

RUN mkdir /home/ccmmdb/data
VOLUME /home/ccmmdb/data

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8


EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
