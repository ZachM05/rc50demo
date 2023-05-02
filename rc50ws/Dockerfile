FROM python:3.8-alpine

WORKDIR /app

COPY ["requirements.txt", "./"]

# RUN  python -m pip install -r ./requirements.txt --proxy http://proxy.henkelgroup.net:80
RUN  python -m pip install -r ./requirements.txt

EXPOSE 3002

COPY . .

CMD [ "python3", "-u", "/app/main.py" ]