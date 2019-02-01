FROM python:3

ADD __init__.py /
ADD commands.py /
ADD constants.py /
ADD Exceptions.py /
ADD main.py /
ADD not_so_secret.py /

RUN pip install https://github.com/Rapptz/discord.py.git@async

CMD ["python", "./main.py"]

