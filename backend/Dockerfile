FROM python:3.8-slim
RUN apt-get update && \
    apt-get install -y build-essential python-dev redis

ENV LANG C.UTF-8
ENV TZ Asia/Tokyo
WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install uwsgi==2.0.17

COPY ./ /app

RUN chmod u+x /app/prestart.sh
CMD ["bash", "/app/prestart.sh"]

EXPOSE 3031
