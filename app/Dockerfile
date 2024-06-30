FROM python:3.9

WORKDIR /app

COPY . /app

RUN ./install.sh

EXPOSE 8000

CMD ["python", "index.py"]
