# supply-chain-graph

Load the ticker symbols associated with the publically traded manufacturers:

    CREATE CONSTRAINT ticker_idx IF NOT EXISTS ON (t:Ticker) ASSERT (t.manufacturer) IS NODE KEY
    
    LOAD CSV WITH HEADERS FROM 'file:///manufacturer_ticker.csv' AS row
    WITH row
    MERGE(ticker:Ticker {manufacturer: row.manufacturer, exchange: row.exchange, ticker: row.ticker})

    MATCH(i:Inventory)
    WITH i
    MATCH(t:Ticker {manufacturer: i.manufacturer})
    MERGE(i)-[:HAS_TICKER]->(t)



Search phrases:

    Items where address contains $address_substr

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