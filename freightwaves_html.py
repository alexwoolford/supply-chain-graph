from confluent_kafka import Consumer, Producer, KafkaException
import ccloud_lib
import logging
import sys
import json
import os
import requests

# to reset offsets:
# kafka-consumer-groups.sh --bootstrap-server pkc-lzvrd.us-west4.gcp.confluent.cloud:9092
# --command-config config.properties --group freightwaves_html --topic freightwaves-url --reset-offsets
# --to-earliest --execute

SCRAPESTACK_API_KEY = os.getenv("SCRAPESTACK_API_KEY")


def get_html(url):
    params = {'access_key': SCRAPESTACK_API_KEY, 'url': url, 'render_js': 1}
    scrapestack_url = 'http://api.scrapestack.com/scrape'
    response = requests.get(scrapestack_url, params=params)
    return response.content.decode("utf-8")


if __name__ == "__main__":
    conf = ccloud_lib.read_ccloud_config('/Users/alexwoolford/.confluent/python.config')
    conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    conf['group.id'] = 'freightwaves_html'

    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('freightwaves_html')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    consumer = Consumer(conf, logger=logger)
    producer = Producer(conf, logger=logger)

    consumer.subscribe(['freightwaves-url'])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                url_record = json.loads(msg.value())
                url = url_record.get('url')
                html = get_html(url)
                url_record['html'] = html
                producer.produce('freightwaves-html', json.dumps(url_record), url)
                consumer.commit()

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
