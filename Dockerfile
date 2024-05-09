FROM ubuntu:22.04

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

RUN apt update
RUN apt install -y apt-utils curl apache2 apache2-utils
RUN apt -y install python3 libapache2-mod-wsgi-py3
RUN ln /usr/bin/python3 /usr/bin/python
RUN apt -y install python3-pip
RUN apt -y install python3.10-venv
RUN pip install --upgrade pip
RUN pip install django ptvsd
RUN a2enmod wsgi
RUN pip install setuptools
RUN pip install wheel
RUN apt install -y pkg-config
RUN apt install -y libmysqlclient-dev

# Copy the dependencies file to the working directory
COPY requirements.txt /app/

RUN pip install -r requirements.txt --no-cache-dir

COPY . /app/

RUN chmod 775 /app
RUN chmod 775 /app/PEMA
RUN chmod 775 /app/prestamos
RUN chmod 775 /app/PEMA/static
RUN chmod 775 /app/static
RUN chmod 775 /app/prestamos/wsgi.py
RUN chmod 775 /app/media

#RUN chgrp -R www-data /app
#RUN chmod -R 2750 /app

RUN a2ensite 000-default.conf
#RUN a2dissite 000-default.conf

EXPOSE 80
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
