FROM ubuntu:latest
ENV PYTHONBUFFERED=1
RUN mkdir /DJANGO_WEBAPP
WORKDIR /DJANGO_WEBAPP
RUN apt update && apt upgrade -y && apt install -y git sudo build-essential 
COPY . /DJANGO_WEBAPP
SHELL ["/bin/bash", "-c"]
RUN ln -s /usr/share/zoneinfo/America/Asuncion /etc/localtime
RUN /DJANGO_WEBAPP/first_start.sh
CMD ["bash"]
