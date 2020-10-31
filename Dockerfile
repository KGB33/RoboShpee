FROM python

RUN apt-get update && \
        apt-get upgrade -y

RUN python -m pip install --upgrade pip
RUN python -m pip install poetry

COPY poetry.lock .
COPY pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY src ./src

CMD ["python", "-m", "src"]
