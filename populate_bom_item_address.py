import pandas as pd
from neo4j import GraphDatabase
import os

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Neo4j DB connection
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# create indexes
index_statements = ["CREATE CONSTRAINT bom_idx IF NOT EXISTS ON (b:BOM) ASSERT (b.bom) IS NODE KEY",
                    "CREATE CONSTRAINT item_idx IF NOT EXISTS ON (i:Item) ASSERT (i.item) IS NODE KEY",
                    "CREATE CONSTRAINT address_idx IF NOT EXISTS ON (a:Address) ASSERT (a.full_address) IS NODE KEY",
                    "CREATE CONSTRAINT part_idx IF NOT EXISTS ON (p:Part) ASSERT (p.manufacturer, p.mpn, p.source) IS NODE KEY",
                    "CREATE FULLTEXT INDEX address_fulltext_idx IF NOT EXISTS FOR (a:Address) ON EACH [a.full_address, a.country, a.state, a.city]",
                    "CREATE FULLTEXT INDEX part_fulltext_idx IF NOT EXISTS FOR (p:Part) ON EACH [p.manufacturer, p.mpn, p.source]"]

with driver.session(database="supplychain") as session:
    for index_statement in index_statements:
        session.run(index_statement)

# load data from spreadsheet
xlsx_path = 'data/Medtronic_BMs_Z2 Report.xlsx'


mpn_analysis_df = pd.read_excel(xlsx_path, 'MPN Analysis')

# load BOM/item nodes and relationships
for index, row in mpn_analysis_df.iterrows():
    bom = str(row["BOM Name"])
    item = str(row["Item Number"])
    with driver.session(database="supplychain") as session:
        session.run("""
                    MERGE(bom:BOM {bom: $bom}) 
                    MERGE(item:Item {item: $item}) 
                    MERGE(bom)-[:HAS_ITEM]->(item) 
                    """,
                    bom=bom,
                    item=item)

# load item/supplier nodes and relationships (Z2 data)
for index, row in mpn_analysis_df.iterrows():
    item = str(row["Item Number"])
    manufacturer = str(row["Z Supplier"])
    mpn = str(row["Z Part Number"])
    with driver.session(database="supplychain") as session:
        session.run("""
                    MERGE(item:Item {item: $item}) 
                    MERGE(part:Part {manufacturer: $manufacturer, mpn: $mpn, source: 'Z2Data'})
                    MERGE(item)-[:HAS_PART]->(part) 
                    """,
                    item=item,
                    manufacturer=manufacturer,
                    mpn=mpn)


# load item/supplier nodes and relationships (original Medtronic data)
for index, row in mpn_analysis_df.iterrows():
    item = str(row["Item Number"])
    manufacturer = str(row["Mfr. Name"])
    mpn = str(row["Mfr. Part Number"])
    with driver.session(database="supplychain") as session:
        session.run("""
                    MERGE(item:Item {item: $item}) 
                    MERGE(part:Part {manufacturer: $manufacturer, mpn: $mpn, source: 'Medtronic'})
                    MERGE(item)-[:HAS_PART]->(part) 
                    """,
                    item=item,
                    manufacturer=manufacturer,
                    mpn=mpn)


# load item/address nodes and relationships
part_locations_df = pd.read_excel(xlsx_path, 'Part Locations')
for index, row in part_locations_df.iterrows():
    item = str(row["Part #"])
    full_address = str(row["FullAddress"])
    country = str(row["Country"])
    state = str(row["State"])
    city = str(row["City"])
    if len(full_address) > 0:
        try:
            with driver.session(database="supplychain") as session:
                session.run("""
                            MERGE(item:Item {item: $item}) 
                            MERGE(address:Address {full_address: $full_address}) 
                            SET address.country = $country 
                            SET address.state = $state 
                            SET address.city = $city 
                            SET address.source = 'Z2Data'
                            MERGE(item)-[:HAS_ADDRESS]->(address) 
                            """,
                            item=item,
                            full_address=full_address,
                            country=country,
                            state=state,
                            city=city
                )
        except Exception as err:
            print(err)
