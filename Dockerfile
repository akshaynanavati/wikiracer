FROM python:3.6.2-jessie

# Create main source directory
RUN mkdir /app
WORKDIR /app

# Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip3.6 install --upgrade pip
RUN pip3.6 install pip-tools
RUN pip-sync

COPY src /app/src

WORKDIR /app/src
ENTRYPOINT ["python3.6"]
CMD ["server.py", "80"]
EXPOSE 80
