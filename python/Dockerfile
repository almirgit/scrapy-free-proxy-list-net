# As Scrapy runs on Python, I choose the official Python 3 Docker image.
#FROM python:3
# Python 3.9.7
FROM python:3.10-alpine

# Set the working directory to /usr/src/app.
WORKDIR /usr/src/app

#RUN apt-get update && apt-get -y install cron vim swaks
# alpine:
RUN apk update
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add perl swaks
RUN pip3 install scrapy==2.10.1 sentry_sdk==1.30.0 pyyaml==6.0.1 psycopg2-binary==2.9.7

# Create output dir
RUN mkdir -p /app-proxy/data
RUN mkdir -p /app-proxy/config

## Copy the file from the local host to the filesystem of the container at the working directory.
#COPY requirements.txt ./

### Install Scrapy specified in requirements.txt.
##RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the project source code from the local host to the filesystem of the container at the working directory.
COPY . .
#RUN rm python-modules
#ADD ../../python-modules python-modules

# Run
#CMD ["./main.py"]
# -u (unbuffered)
CMD ["python", "-u", "main.py"]
#CMD ["python", "-u", "sleep.py"]

