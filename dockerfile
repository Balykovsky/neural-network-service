FROM python:3.6

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /code/
WORKDIR /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary
COPY . /code/
EXPOSE 8585
