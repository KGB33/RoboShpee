FROM python

ADD bot/__init__.py /
ADD bot/constants.py /
ADD bot/Exceptions.py /
ADD bot/main.py /

RUN pip install discord.py

CMD ["python", "./main.py"]
