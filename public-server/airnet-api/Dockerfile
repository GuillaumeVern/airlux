FROM python:3.13

WORKDIR /

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./app ./app

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]