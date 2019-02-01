FROM python:3

ADD 33bot/__init__.py /
ADD 33bot/commands.py /
ADD 33bot/constants.py /
ADD 33bot/Exceptions.py /
ADD 33bot/main.py /
ADD 33bot/discord /

RUN pip install https://github.com/Rapptz/discord.py/tree/async

CMD ["python", "./33bot/main.py"]

