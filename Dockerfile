FROM python

ADD 33bot/__init__.py /
ADD 33bot/constants.py /
ADD 33bot/Exceptions.py /
ADD 33bot/main.py /

RUN pip install discord.py

CMD ["python", "./main.py"]

