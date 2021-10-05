# supply-chain-graph

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
