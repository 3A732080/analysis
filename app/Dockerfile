FROM python:3.9

WORKDIR /app

COPY . /app

# RUN ./install.sh
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_md
RUN python -m spacy download en_core_web_trf

EXPOSE 8000

CMD ["python", "index.py"]
