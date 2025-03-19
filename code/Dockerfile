FROM python:3.12

LABEL "com.qurtesy.finance"="Qurtesy"
LABEL version="1.0"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD ["fastapi", "run", "main.py", "--port", "8000"]