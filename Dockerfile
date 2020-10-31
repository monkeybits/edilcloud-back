FROM python:3.5
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN mkdir /office2017.whistle.it
WORKDIR /office2017.whistle.it
COPY requirements.txt /office2017.whistle.it/
RUN apt-get install gcc
RUN pip install psycopg2
RUN pip install -r requirements.txt
COPY . /office2017.whistle.it/
ADD entrypoint.sh /entrypoint.sh
ADD entrypoint_redis.sh /entrypoint_redis.sh
RUN chmod a+x /entrypoint.sh
RUN chmod a+x /entrypoint_redis.sh
ENTRYPOINT ["/entrypoint.sh"]
RUN cd /var/log/ && mkdir django && touch whistle-api_exceptions.log