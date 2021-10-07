import pandas as pd
from selenium import webdriver
import re


def get_text_from_page(url):
    driver = webdriver.Chrome()
    driver.get(url)
    page_text = driver.find_element_by_tag_name("body").text
    driver.close()
    return page_text


urls_df = pd.read_csv("10k_urls.csv")

for index, row in urls_df.iterrows():
    exchange = row['exchange']
    ticker = row['ticker']
    url_10k = row['url_10k']

    text_10k = get_text_from_page(url_10k)

    try:
        # the regex below didn't work for the following tickers: DIOD, HON, KEM, MMM, MXIM, NXPI, TXN
        risk_text = re.search(r'Signatures.*Item 1A(.*?)Item 1B', text_10k, re.DOTALL | re.IGNORECASE).group(1)
        f = open("data/10k_risk_text/{ticker}.txt".format(ticker=ticker), "w+")
        f.writelines(risk_text)
        f.close()
    except Exception as err:
        print("Unable to parse risk from 10k for ticker {ticker}".format(ticker=ticker), err)
