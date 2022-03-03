import requests
import urllib.parse
import json
import pandas as pd
from confluent_kafka import Producer
import ccloud_lib
import freightwaves_existing_urls


def get_article_urls():
    cdx_url = 'http://web.archive.org/cdx/search/cdx'
    search_url_prefix = 'freightwaves.com/'
    search_url_suffix = "?p="
    search_url = search_url_prefix + urllib.parse.quote_plus(search_url_suffix)

    params = {'url': search_url, 'matchType': 'prefix', 'output': 'json'}

    response = requests.get(cdx_url, params=params)
    data = json.loads(response.content)

    columns = data[0]
    data = data[1:]

    dataframe = pd.DataFrame(data)
    dataframe.columns = columns

    dataframe['id'] = pd.to_numeric(dataframe.original.str.extract(r'([0-9]+)', expand=False))
    dataframe = dataframe.sort_values(by=['id'])
    dataframe = dataframe.drop_duplicates(subset=['id', 'original'])
    dataframe = dataframe[['id', 'original']]

    return list(dataframe.original)


if __name__ == "__main__":
    existing_urls = freightwaves_existing_urls.get_existing_urls()
    # get 10k most recent urls
    urls = get_article_urls()
    urls = urls[-10000:]
    urls.reverse()

    conf = ccloud_lib.read_ccloud_config('/Users/alexwoolford/.confluent/python.config')
    producer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    producer = Producer(producer_conf)

    for url in urls:
        if not url in existing_urls:
            url_json = json.dumps({'url': url})
            producer.produce('freightwaves-url', url_json, url)

    producer.flush()
