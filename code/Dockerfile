FROM python:3.12

LABEL "com.qurtesy.finance"="Qurtesy"
LABEL version="1.0"

WORKDIR /code

COPY ./_requirements /code/_requirements

RUN pip install --no-cache-dir --upgrade -r /code/_requirements/dev.txt

COPY . /code

CMD ["fastapi", "run", "main.py", "--port", "8000"]