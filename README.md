# supply-chain-graph

Load the ticker symbols associated with the publicly traded manufacturers, and 10k urls (US-only):

    CREATE CONSTRAINT IF NOT EXISTS ON (t:Ticker)
    ASSERT (t.exchange, t.ticker) IS NODE KEY

    LOAD CSV WITH HEADERS FROM 'file:///manufacturer_ticker.csv' AS row
    WITH row
    MERGE(ticker:Ticker {exchange: row.exchange, ticker: row.ticker})

    LOAD CSV WITH HEADERS FROM 'file:///manufacturer_ticker.csv' AS row
    WITH row
    MATCH(i:Inventory)
    WHERE i.manufacturer = row.manufacturer
    WITH row, i
    MATCH(t:Ticker)
    WHERE t.ticker = row.ticker
    AND t.exchange = row.exchange
    MERGE(i)-[:MANUFACTURER_HAS_TICKER]->(t)

    LOAD CSV WITH HEADERS FROM 'file:///10k_urls.csv' AS row
    MATCH(t:Ticker)
    WHERE t.ticker = row.ticker
    AND t.exchange = row.exchange
    SET t.url_10k = row.url_10k


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