import boto3
import glob
from pathlib import Path
from funcy import project


def get_entities_from_text(text):
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')
    return comprehend.detect_entities(Text=text, LanguageCode='en')


def get_chunks(text, maxlength):
    start = 0
    end = 0
    while start + maxlength < len(text) and end != -1:
        end = text.rfind(".", start, start + maxlength + 1)
        yield text[start:end]
        start = end + 1
    yield text[start:]


risk_text_files = glob.glob("data/10k_risk_text/*")

for risk_text_file in risk_text_files:
    fh = open(risk_text_file, 'r')
    text = fh.read()

    chunks = get_chunks(text, 4500)

    ticker = Path(risk_text_file).stem

    all_entities = list()
    for chunk in chunks:
        entities = get_entities_from_text(text=chunk).get('Entities')
        entities = [dict(entity, **{'Ticker': ticker}) for entity in entities]

        fields_to_capture = ['Type', 'Text', 'Ticker']
        entities = [project(entity, fields_to_capture) for entity in entities]

        all_entities += entities

    pass

