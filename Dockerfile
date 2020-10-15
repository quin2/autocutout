FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app

RUN pip install -r /app/requirements.txt

RUN apt update -y
RUN apt install intltool imagemagick libmagickcore-dev pstoedit libpstoedit-dev autopoint -y

RUN git clone https://github.com/autotrace/autotrace.git && cd autotrace && ./autogen.sh && LD_LIBRARY_PATH=/usr/local/lib ./configure --prefix=/usr && make && make install
