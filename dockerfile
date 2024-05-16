FROM python:3.9
WORKDIR /app
COPY . /app 
#copy the files to ./app

RUN pip install --no-cache-dir -r requirements.txt
#install dependencies


EXPOSE 3001

CMD ["python3","miner.py"]

