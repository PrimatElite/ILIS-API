FROM python:3.6.6

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY app/ ./app/

COPY app_main.py ./app_main.py

COPY startup.sh ./startup.sh
RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

COPY VERSION ./VERSION

EXPOSE 5000

CMD ["./startup.sh"]
