from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import os
from functools import wraps
import redis
import json
from neo4j import GraphDatabase


# Redis for caching of API calls
global r
r = redis.Redis(host='deepthought.woolford.io', port=6379, db=0)


def cache(function=None):
    """
    This function is a decorator to cache the results from the Octopart API in Redis.

    This is to avoid burning through API credits by making duplicate calls during development.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        q = args[0]

        val = r.get(q)

        if val:
            return json.loads(val)
        else:

            _ = function(*args, **kwargs)
            r.set(str(q), json.dumps(_))
            return _

    return wrapper


@cache
def get_part_inventory_from_octopart(q):

    transport = AIOHTTPTransport(url="https://octopart.com/api/v4/endpoint", headers={'token': os.getenv('OCTOPART_TOKEN')})
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(
        """
        query ($q: String!) {
          search(q: $q, in_stock_only: true) {
            results {
              part {
                mpn
                manufacturer {
                  name
                }
                short_description
                total_avail
              }
            }
          }
        }
    """)

    params = {"q": q}
    result = client.execute(query, variable_values=params)

    if result.get("search").get("results"):
        return [part.get("part") for part in result.get("search").get("results")]


if __name__ == "__main__":

    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    # Neo4j DB connection
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    parts = list()
    with driver.session(database="supplychain") as session:
        result = session.run("""MATCH (part:Part) RETURN part""")
        for elem in result:
            manufacturer = elem.get("part").get("manufacturer")
            mpn = elem.get("part").get("mpn")
            parts.append({"manufacturer": manufacturer, "mpn": mpn})

    for part in parts:
        octopart_inventory_parts = get_part_inventory_from_octopart(part.get("manufacturer") + " " + part.get("mpn"))
        if octopart_inventory_parts:
            for octopart_inventory_part in octopart_inventory_parts:

                octopart_inventory_manufacturer = octopart_inventory_part.get("manufacturer").get("name")
                octopart_inventory_mpn = octopart_inventory_part.get("mpn")
                octopart_inventory_description = octopart_inventory_part.get("short_description")
                octopart_inventory_total_avail = octopart_inventory_part.get("total_avail")

                with driver.session(database="supplychain") as session:
                    session.run("""
                                MATCH(part:Part {manufacturer: $manufacturer, mpn: $mpn})
                                MERGE(octopart:Inventory {manufacturer: $octopart_inventory_manufacturer, mpn: $octopart_inventory_mpn})
                                SET octopart.description = $octopart_inventory_description
                                SET octopart.total_avail = $octopart_inventory_total_avail
                                MERGE(part)-[:HAS_INVENTORY]->(octopart)
                                """,
                                manufacturer=manufacturer,
                                mpn=mpn,
                                octopart_inventory_manufacturer=octopart_inventory_manufacturer,
                                octopart_inventory_mpn=octopart_inventory_mpn,
                                octopart_inventory_description=octopart_inventory_description,
                                octopart_inventory_total_avail=octopart_inventory_total_avail
                                )

