FROM python:3.12

LABEL "com.qurtesy.finance"="Qurtesy"
LABEL version="1.0"

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /code

COPY ./_requirements /code/_requirements

RUN pip install --no-cache-dir --upgrade -r /code/_requirements/dev.txt

COPY . /code

# CMD ["fastapi", "run", "main.py", "--port", "8000"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085", "--workers", "1"]