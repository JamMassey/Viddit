FROM python:3.9-slim as build

ENV PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code
COPY setup.py setup.cfg pyproject.toml /code/
COPY src /code/src

# Install chrome and chrome driver
RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 wget unzip gnupg \
    && apt-get install -y curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update \
    && apt-get install -y google-chrome-stable \
    && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
    && unzip -o -q /tmp/chromedriver.zip -d /code/src/viddit/resources \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set display port to avoid crash
ENV DISPLAY=:99

FROM python:3.9-slim as final
WORKDIR  /code

COPY --from=build --chown=appuser:appgroup /code/* .
COPY --from=build --chown=appuser:appgroup /code/src/viddit/resources/chromedriver /code/src/viddit/resources/chromedriver
RUN set -ex \
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    && chown -R appuser:appgroup /code \
    && pip install wheel \
    && pip install . \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

CMD [ "python3", "src/viddit" ]
USER appuser


#, "--subreddits", "$SUBREDDITS", "--max-comments", "$MAX_COMMENTS", "--max-vids-




# FROM python:3.9-slim as build
# #.12-buster
# ENV PIP_DEFAULT_TIMEOUT=100 \
#     # Allow statements and log messages to immediately appear
#     PYTHONUNBUFFERED=1 \
#     # disable a pip version check to reduce run-time & log-spam
#     PIP_DISABLE_PIP_VERSION_CHECK=1 \
#     # cache is useless in docker image, so disable to reduce image size
#     PIP_NO_CACHE_DIR=1

# WORKDIR /code
# COPY . /code


# RUN apt-get update
# RUN apt-get install ffmpeg libsm6 libxext6  -y


# # Install Chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN apt-get -y update
# RUN apt-get install -y google-chrome-stable

# # Install and unzip chromedriver
# RUN apt-get install -yqq unzip
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /code/src/viddit/resources

# # Set display port to avoid crash
# ENV DISPLAY=:99

# FROM python:3.9-slim as final
# WORKDIR  /code

# COPY --from=build  /code/* .
# RUN set -ex \
#     # Create a non-root user
#     && addgroup --system --gid 1001 appgroup \
#     && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
#     # Install dependencies
#     && pip install . \
#     # Clean up
#     && apt-get autoremove -y \
#     && apt-get clean -y \
#     && rm -rf /var/lib/apt/lists/*

# CMD [ "python3", "src/viddit" ]
# #, "--subreddits", "$SUBREDDITS", "--max-comments", "$MAX_COMMENTS", "--max-vids-per-subreddit", "$MAX_VIDEOS", "--operating-system", "linux",  "--no-local-mode"]
# USER appuser