FROM node:12-alpine
RUN apk update
RUN apk add openssh
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install update
RUN pip install termcolor
RUN pip install requests
RUN pip install os
RUN pip install sys
CMD ["/bin/sh"]
