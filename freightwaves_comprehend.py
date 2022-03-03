
from confluent_kafka import Consumer, Producer, KafkaException
import ccloud_lib
import logging
import sys
import boto3
import json
import textwrap
import dateutil.parser

REGION = 'us-west-2'

if __name__ == "__main__":
    conf = ccloud_lib.read_ccloud_config('/Users/alexwoolford/.confluent/python.config')
    conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    conf['group.id'] = 'freightwaves_comprehend'

    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('freightwaves_comprehend')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    # comprehend_detect = ComprehendDetect()
    comprehend = boto3.client('comprehend', region_name=REGION)

    consumer = Consumer(conf, logger=logger)
    producer = Producer(conf, logger=logger)

    consumer.subscribe(['freightwaves-article'])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                article_record = json.loads(msg.value())
                url = article_record.get('url')
                article_body = article_record.get('articleBody')

                for article_body_chunk in textwrap.wrap(article_body, 4500, break_long_words=False):
                    response = comprehend.detect_entities(Text=article_body_chunk, LanguageCode='en')
                    entities = response.get('Entities')
                    for entity in entities:
                        if entity.get('Score') > 0.8 and entity.get('Type') not in ['QUANTITY', 'DATE']:
                            entity_type = entity.get('Type').capitalize()
                            entity_text = entity.get('Text')
                            article_timestamp = article_record.get('datePublished')
                            article_timestamp_parsed_time = dateutil.parser.parse(article_timestamp)
                            timestamp = int(article_timestamp_parsed_time.timestamp() * 1000)
                            entity_record = {'url': url, 'entityType': entity_type, 'entityValue': entity_text, 'timestamp': timestamp}
                            producer.produce('freightwaves-entity', json.dumps(entity_record))

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
