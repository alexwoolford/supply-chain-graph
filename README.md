# supply-chain-graph

Load the ticker symbols associated with the publicly traded manufacturers, and 10k urls (US-only):

    CREATE CONSTRAINT IF NOT EXISTS ON (t:Ticker)
    ASSERT (t.exchange, t.ticker) IS NODE KEY

    LOAD CSV WITH HEADERS FROM 'file:///manufacturer_ticker.csv' AS row
    WITH row
    MERGE(ticker:Ticker {exchange: row.exchange, ticker: row.ticker})

    LOAD CSV WITH HEADERS FROM 'file:///manufacturer_ticker.csv' AS row
    WITH row
    MATCH(p:Part)
    WHERE p.manufacturer = row.manufacturer
    WITH row, p
    MATCH(t:Ticker)
    WHERE t.ticker = row.ticker
    AND t.exchange = row.exchange
    MERGE(p)-[:MANUFACTURER_HAS_TICKER]->(t)

    LOAD CSV WITH HEADERS FROM 'file:///10k_urls.csv' AS row
    MATCH(t:Ticker)
    WHERE t.ticker = row.ticker
    AND t.exchange = row.exchange
    SET t.url_10k = row.url_10k

## delete insignificant nodes from NLP

Delete all the uninteresting organization nodes.

    MATCH(o:Organization)
    WHERE NOT o.text IN
    [
      '3TG',
      'AMD',
      'AgigA',
      'Amphenol',
      'Apple, Inc.',
      'Atmel',
      'Cypress',
      'Eaton',
      'Enovix',
      'Enovix Corporation',
      'Deca',
      'Deca Technologies Inc.',
      'DRC',
      'GF',
      'GLOBALFOUNDRIES, Inc.',
      'Higon Information Technology Co., Ltd.',
      'Huawei',
      'Huawei Technologies',
      'Huawei Technologies Co., Ltd.',
      'IFX Merger Sub, Inc.',
      'IMFT',
      'ITW',
      'Illinois Tool Works Inc.',
      'Infineon',
      'Infineon Technologies AG',
      'Inotera',
      'Intel',
      'Intel Corporation',
      'Kioxia Holdings Corporation',
      'MTS',
      'MTS Systems Corporation',
      'MTS T',
      'MTS T&S',
      'MTS Test & Simulation',
      'Maxim',
      'Maxim Integrated Products, Inc.',
      'Microchip',
      'Micron',
      'Micron B.V.',
      'Micron and Micron Semiconductor B.V.',
      'Microsemi',
      'NAND',
      'Nvidia Corporation',
      'PSoC®',
      'Qimonda',
      'SAMR',
      'SK Hynix Inc.',
      'SK hynix Inc.',
      'SK hynix system ic Inc.',
      'SKH',
      'SKHS',
      'Samsung Electronics Co., Ltd.',
      'Semtech',
      'SkyHigh',
      'SkyHigh Memory Limited',
      'Sony',
      'Spansion',
      'Spansion Inc.',
      'SuperFlash',
      'TSMC',
      'Taiwan Semiconductor Manufacturing Company',
      'Taiwan Semiconductor Manufacturing Company Limited',
      'Tongfu Microelectronics Co., Ltd.',
      'Toshiba Memory Corporation',
      'VPG',
      'Vishay',
      'Vishay Intertechnology, Inc.',
      'Vishay Precision Group',
      'Western Digital Corporation',
      'Xilinx',
      'Xilinx, Inc.',
      'ZTE'
    ]
    DETACH DELETE o

Delete all the uninteresting `:Other` nodes:

    MATCH(o:Other)
    WHERE NOT o.text IN
    [
      'COVID-19',
      'COVID-19 pandemic',
      'Preferred Supply Program',
      'Tantalum',
      'SARS-CoV'
    ]
    DETACH DELETE o

Delete all the bad `:Location`:

    MATCH(l:Location)
    WHERE l.text IN
    [
      'States',
      'Deca',
      'China.Many',
      'Great British Pound, Switzerland',
      'Korean',
      'European',
      'Republic'
    ]
    DETACH DELETE l

Create NLP node indexes:

    CREATE FULLTEXT INDEX organization_fulltext_idx IF NOT EXISTS FOR (o:Organization) ON EACH [o.text]
    CREATE FULLTEXT INDEX location_fulltext_idx IF NOT EXISTS FOR (l:Location) ON EACH [l.text]
    CREATE FULLTEXT INDEX other_fulltext_idx IF NOT EXISTS FOR (o:Other) ON EACH [o.text]



Search phrases:

    Items where address contains $address_substr

    :params {address_substr: 'Israel'}

    MATCH(a:Address)-[r]-(i:Item)
    WHERE a.full_address contains $address_substr
    RETURN a, r, i

[//]: # (TODO: find longest chain and navigate up the chain w/ Bloom)
[//]: # (TODO: add parametric attributes and match)
[//]: # (TODO: geo-filter based on lat/lon)
[//]: # (TODO: review other attributes in Z2 spreadsheet and add to graph)
[//]: # (TODO: consider adding Octopart, or Digikey attributes)
[//]: # (TODO: review other potential datasources on ProgrammableWeb)
[//]: # (TODO: add 10k and news feed relationship narrative)
[//]: # (TODO: find examples of automotive shortages)
[//]: # (TODO: capture 10k reports for tickers and perform entity resolution)
[//]: # (TODO: add requirements.txt)
[//]: # (TODO: fix 10k risk parser for DIOD, HON, KEM, MMM, MXIM, NXPI, TXN)
[//]: # (TODO: incorporate RSS newsfeed article evaluation)
[//]: # (TODO: steps to recreate graph; spell out environment variable properties and script order)

