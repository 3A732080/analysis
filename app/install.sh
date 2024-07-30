#!/bin/bash

pip install --upgrade pip
pip install -r requirements.txt

python -m spacy download en_core_web_md
python -m spacy download en_core_web_trf