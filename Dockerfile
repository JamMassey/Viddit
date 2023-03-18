FROM python:3.9.12-buster

WORKDIR /code

RUN apt-get update
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN python3 -m pip install --upgrade pip
COPY . /code
RUN pip3 install .

EXPOSE 9128
ENTRYPOINT [ "python3", "viddit" ]
