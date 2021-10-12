import boto3
import glob
from pathlib import Path
from funcy import project
import pandas as pd
from neo4j import GraphDatabase
import os

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

all_entities = list()
for risk_text_file in risk_text_files:
    fh = open(risk_text_file, 'r')
    text = fh.read()

    chunks = get_chunks(text, 4500)

    ticker = Path(risk_text_file).stem

    for chunk in chunks:
        entities = get_entities_from_text(text=chunk).get('Entities')
        entities = [dict(entity, **{'Ticker': ticker}) for entity in entities]

        fields_to_capture = ['Type', 'Text', 'Ticker']
        entities = [project(entity, fields_to_capture) for entity in entities]

        all_entities += entities

all_entities_df = pd.DataFrame(all_entities)

all_entities_df['Type'] = all_entities_df['Type'].apply(lambda x: x.capitalize())

entity_types_to_keep = ['Location', 'Organization', 'Other']
all_entities_df = all_entities_df.query("Type in @entity_types_to_keep")

all_entities_df = all_entities_df.rename(columns={'Type': 'label', 'Text': 'text', 'Ticker': 'ticker'})


neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Neo4j DB connection
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

for index, row in all_entities_df.iterrows():
    label = str(row["label"])
    text = str(row["text"])
    ticker = str(row["ticker"])
    cypher = """MATCH(t:Ticker)
                WHERE t.ticker = $ticker 
                MERGE(x:{label} {{text: $text}})
                MERGE(t)-[:HAS_RISK]->(x) 
                """.format(label=label)
    with driver.session(database="supplychain") as session:
        session.run(cypher,
                    label=label,
                    text=text,
                    ticker=ticker)


