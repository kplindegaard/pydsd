FROM python:3.7-alpine

COPY *.py /app/
COPY requirements.txt /app/
COPY wait-for /app

WORKDIR /app

RUN chmod a+x wait-for
RUN pip install -r requirements.txt

# By default, position.py will start.
CMD ["python3", "position.py"]
