FROM python

RUN apt-get update && \
        apt-get upgrade -y

RUN python -m pip install --upgrade pip

COPY pyproject.toml .
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY src ./src

CMD ["python", "-m", "src"]
