FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /var/www/webapp
WORKDIR /var/www/webapp
ADD requirements.txt /var/www/webapp/
RUN apt-get install libjpeg62-turbo-dev zlib1g-dev
RUN dpkg -L libjpeg62-turbo-dev
RUN ln -s /usr/lib/arm-linux-gnueabi/libz.so /usr/lib/libz.so
RUN ln -s /usr/lib/arm-linux-gnueabi/libjpeg.a /usr/lib/libjpeg.a
RUN pip install -r requirements.txt
ADD . /var/www/webapp/