# 3.9 т. к. старый проект
FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# пусть будет публичным
ENV BOT_TOKEN="1703612469:AAFvb-vSuFrYwF8mvU2oPi-9p9hx0k1GnVc"

# Run the bot
CMD ["python", "main.py"]