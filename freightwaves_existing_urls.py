from confluent_kafka import Consumer, KafkaException, TopicPartition
import ccloud_lib
import logging
import json
import sys
import uuid


def get_existing_urls():

    urls = set()

    conf = ccloud_lib.read_ccloud_config('/Users/alexwoolford/.confluent/python.config')
    conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    conf['group.id'] = 'freightwaves_urls_new_{uuid}'.format(uuid=str(uuid.uuid4())[:8])
    conf['auto.offset.reset'] = 'smallest'
    # 'auto.offset.reset': 'smallest'

    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('freightwaves_urls_new')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    consumer = Consumer(conf, logger=logger)

    consumer.subscribe(["freightwaves-url"])

    count = 0
    topic_partition = TopicPartition("freightwaves-url", partition=0)
    start_offset, end_offset = consumer.get_watermark_offsets(topic_partition)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                url_record = json.loads(msg.value())
                count += 1
                urls.add(url_record.get('url'))
                if count == end_offset:
                    break

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

    return urls


if __name__ == "__main__":
    urls = get_existing_urls()
