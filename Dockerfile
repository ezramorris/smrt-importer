FROM python:3.9

WORKDIR /app

# Install dependencies so this doesn't have to be run
# every time the code changes.
COPY pyproject.toml setup.cfg setup.py /app/
RUN mkdir smrt_importer && \
    python setup.py egg_info && \
    pip install -r smrt_importer.egg-info/requires.txt

# Install the actual package.
COPY config.ini /app/
COPY smrt_importer /app/smrt_importer/
RUN pip install -e .

CMD ["smrt-importer"]
