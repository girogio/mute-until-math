FROM python:3.12.7-slim-bookworm

RUN apt update
RUN apt install -y git autoconf automake libtool gcc make ffmpeg 
RUN apt install wget

RUN git clone https://github.com/xiph/opus /opus --depth=1

WORKDIR /opus

RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
