FROM python:3.6.2-jessie

# Create main source directory
RUN mkdir /app
WORKDIR /app
COPY titles.txt /app/titles.txt
COPY load_test.py /app/load_test.py

WORKDIR /app
ENTRYPOINT ["python3.6"]
CMD ["load_test.py", "100000"]
