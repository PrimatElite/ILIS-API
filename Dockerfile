FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY app/ ./app/

COPY main.py ./main.py

COPY startup.sh ./startup.sh
RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

COPY VERSION ./VERSION

EXPOSE 5000

CMD ["./startup.sh"]
