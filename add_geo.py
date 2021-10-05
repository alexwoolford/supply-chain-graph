import requests
import json
from neo4j import GraphDatabase
import os

google_geocode_api_key = os.getenv("GOOGLE_GEOCODE_API_KEY")

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Neo4j DB connection
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


def get_location_for_address(address):
    params = {"key": google_geocode_api_key, "address": address}
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = json.loads(response.content)
        if results.get('status') == 'OK':
            if results.get('results'):
                if len(results.get('results')) > 0:
                    result = results.get('results')[0]
                    if result.get('geometry'):
                        geometry = result.get('geometry')
                        if geometry.get('location'):
                            location = geometry.get('location')
                            return location


if __name__ == "__main__":

    addresses = list()
    with driver.session(database="supplychain") as session:
        result = session.run("""MATCH (address:Address) RETURN address""")
        for elem in result:
            address = elem.get('address').get('full_address')
            addresses.append(address)

    for address in addresses:
        location = get_location_for_address(address)
        if location:
            with driver.session(database="supplychain") as session:
                session.run("""
                            MATCH(full_address:Address {full_address: $address}) 
                            SET full_address.latitude = $latitude 
                            SET full_address.longitude = $longitude""",
                            address=address,
                            latitude=location.get("lat"),
                            longitude=location.get("lng"))
