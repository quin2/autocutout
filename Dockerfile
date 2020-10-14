FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app

RUN pip install -r app/requirements.txt

RUN wget https://github.com/autotrace/autotrace/releases/download/travis-20200219.65/autotrace_0.40.0-20200219_all.deb -O autotrace_0.40.0-20200219_all.deb

RUN dpkg -i autotrace_0.40.0-20200219_all.deb

RUN apt-get install -y -f

