FROM python:3.12

WORKDIR /code

COPY ./code/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./code/app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]