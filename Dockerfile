FROM python:3.10
WORKDIR /bot
COPY requirements.txt /bot/ /operators/
RUN pip install -r requirements.txt
COPY . /bot
CMD python bot.py