FROM python:3.11.14

WORKDIR /app
COPY ./configs ./connfigs
COPY ./trade_api ./trade_api
COPY ./manage.py ./manage.py
COPY ./requirements.txt ./requirements.txt

RUN python3 -m venv venv
RUN source venv/bin/activate
RUN pip install -r requirements.txt
RUN python manage.py migrate trade_api
RUN python manage.py runserver
