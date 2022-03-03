from confluent_kafka import Consumer, KafkaException
import ccloud_lib
import logging
import json
import sys
import os
from neo4j import GraphDatabase


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

if __name__ == "__main__":

    # Neo4j DB connection
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session(database=NEO4J_DATABASE) as session:

        conf = ccloud_lib.read_ccloud_config('/Users/alexwoolford/.confluent/python.config')
        conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
        conf['group.id'] = "freightwaves_entity_neo4j"

        # Create logger for consumer (logs will be emitted when poll() is called)
        logger = logging.getLogger('freightwaves_entity_neo4j')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)

        consumer = Consumer(conf, logger=logger)

        consumer.subscribe(["freightwaves-entity"])

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                else:
                    entity_record = json.loads(msg.value())
                    url = entity_record.get('url')
                    entity_type = entity_record.get('entityType')
                    entity_value = entity_record.get('entityValue')
                    timestamp = entity_record.get('timestamp')
                    cypher = """MERGE(a:Article {{link: '{url}'}}) MERGE(e:{entity_type} {{text: {entity_value}}}) MERGE(a)-[r:HAS_ENTITY]->(e) SET r.timestamp = {timestamp}""".format(url=url, entity_type=entity_type, entity_value=repr(entity_value), timestamp=timestamp)
                    session.run(cypher)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')

        finally:
            # Close down consumer to commit final offsets.
            consumer.close()
