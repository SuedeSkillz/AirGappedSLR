FROM node:12-alpine
RUN apk update
RUN apk add openssh
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk --no-cache add build-base libffi-dev openssl-dev openssl python3-dev tftp-hpa
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install update
RUN pip install termcolor
RUN pip install requests
RUN pip install netmiko
RUN pip install tftpy
WORKDIR /AirGappedSLR/input
WORKDIR ..
ADD *.csv .
ADD *.ini .
ADD *.py .
ADD *.md .
ADD *.sh .
RUN chmod +x *.sh
ENTRYPOINT "./init.sh" && "/bin/sh"
CMD ["/bin/sh"]
