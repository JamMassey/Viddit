FROM python:3.9 
#.12-buster

WORKDIR /code
COPY . /code


RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y


# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# Install and unzip chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /code/src/viddit/resources

# Set display port to avoid crash
ENV DISPLAY=:99

ARG SUBREDDITS 
ARG MAX_COMMENTS
ARG MAX_VIDEOS


RUN python3 -m pip install --upgrade pip
RUN pip3 install .

CMD [ "python3", "src/viddit", "--subreddits", "$SUBREDDITS", "--max-comments", "$MAX_COMMENTS", "--max-vids-per-subreddit", "$MAX_VIDEOS", "--operating-system", "linux",  "--no-local-mode"]
