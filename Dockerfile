FROM ubuntu:latest
ENV PYTHONBUFFERED=1
RUN mkdir /DJANGO_WEBAPP
WORKDIR /DJANGO_WEBAPP
RUN apt update && apt upgrade -y && apt install -y git sudo build-essential 
SHELL ["/bin/bash", "-c"]
RUN ln -s /usr/share/zoneinfo/America/Asuncion /etc/localtime
COPY ./first_start.sh /DJANGO_WEBAPP
RUN /DJANGO_WEBAPP/first_start.sh
COPY ./requirements.txt /DJANGO_WEBAPP
COPY ./requirements-dev.txt /DJANGO_WEBAPP
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
COPY . /DJANGO_WEBAPP
CMD ["bash"]
