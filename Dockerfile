FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir aiohttp discord.py lxml requests urllib3 matplotlib pytz pycountry dblpy pandas openpyxl redis pymongo motor dnspython

COPY . .

CMD [ "python", "./main.py" ]