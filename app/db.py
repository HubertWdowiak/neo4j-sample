from flask import g
from neo4j import GraphDatabase
import os


def get_db():
    if 'db' not in g:
        g.db = GraphDatabase.driver(
            os.environ['URI'],
            auth=(
                os.environ['USER'],
                os.environ['PASSWORD']
            )
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query(query):
    def do_cypher_tx(tx, cypher):
        result = tx.run(cypher)
        values = []
        for record in result:
            record_data = []
            for i, subrecord in enumerate(record):
                try:
                    prop = subrecord._properties
                    record_data.append(prop)
                except Exception:

                    record_data.append({record._Record__keys[i]: subrecord})
            values.append(record_data)
        return values

    with get_db().session() as session:
        return session.read_transaction(do_cypher_tx, query)
