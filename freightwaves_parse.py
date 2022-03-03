from confluent_kafka import Consumer, Producer, KafkaException
import ccloud_lib
import logging
import json
import sys
from bs4 import BeautifulSoup


def parse_html(html):
    article_properties = None
    try:
        soup = BeautifulSoup(html)
        article = soup.find("article", {"id": "the-post"})
        article_properties = json.loads(article.find("script", {"id": "tie-schema-json"}).contents[0])
    except Exception as err:
        logger.error(err)

    return article_properties


if __name__ == "__main__":

    conf = ccloud_lib.read_ccloud_config('/Users/alexwoolford/.confluent/python.config')
    conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    conf['group.id'] = "freightwaves_parse"

    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('freightwaves_html')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    consumer = Consumer(conf, logger=logger)
    producer = Producer(conf, logger=logger)

    consumer.subscribe(["freightwaves-html"])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                html_record = json.loads(msg.value())
                url = html_record.get('url')
                html = html_record.get('html')
                article = parse_html(html)
                if article:
                    producer.produce('freightwaves-article', json.dumps(article), url)
                    consumer.commit()

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
