FROM python:3

ADD 33bot/__init__.py /
ADD 33bot/commands.py /
ADD 33bot/constants.py /
ADD 33bot/Exceptions.py /
ADD 33bot/main.py /

RUN pip install https://github.com/KGB33/discord.py/archive/async.zip

CMD ["python", "./33bot/main.py"]

