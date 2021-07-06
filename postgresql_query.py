#!/usr/bin/env python

import os
import sys
import psycopg2
import psycopg2.extras
# Use pytoml for older systems (<= Debian 8)
try:
    import toml
except ImportError:
    import pytoml as toml
from line_protocol import make_line


class PGQuerier:
    dsn = None
    conn = None
    default_db = None
    databases = []

    def __init__(self, dsn=None, dbname=None):
        self.dsn = dsn
        self.default_db = dbname
        self.connect()

    def connect(self, dbname=None):
        if not dbname:
            dbname = self.default_db
        self.conn = psycopg2.connect(self.dsn, database=dbname)
        self.conn.set_session(readonly=True, autocommit=True)

    def fetch_databases(self):
        result = self.query(
            "SELECT datname FROM pg_database where datistemplate = false")
        self.databases = [ d['datname'] for d in result ]
        return self.databases

    def query(self, query):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(query)
            result = cur.fetchall()
        except psycopg2.Error as error:
            result = None
            sys.stderr.write(error.pgerror)
            sys.stderr.flush()
        finally:
            cur.close()
        return result

    def per_db_query(self, query, databases=None):
        if not databases:
            databases = self.databases
        results = {}
        for d in databases:
            self.connect(dbname=d)
            result = self.query(query)
            if result:
                results[d] = result
        return results


def format_results(result, dbname=None, measurement=None, tagvalue=""):
    f = []
    tag_keys = tagvalue.split(",")
    if tag_keys == ['']:
        tag_keys = []
    for fields in result:
        if not dbname:
            tags = {}
        else:
            tags = {'datname': dbname}
        for t in tag_keys:
            if t in fields:
                tags[t] = fields.pop(t)
        f1 = make_line(measurement, tags=tags, fields=fields)
        f.append(f1)
    return f


def print_data(pg, conf):

    # TODO: Only fetch databases if per_db is true for any query
    pg.fetch_databases()

    to_print = []

    for q in conf["query"]:
        measurement = q["measurement"]
        if "tagvalue" in q:
            tagvalue = q["tagvalue"]
        else:
            tagvalue = ""

        # Optionally read query from file
        if 'sqlquery' in q:
            query = q['sqlquery']
        elif 'script' in q:
            with open(q['script']) as script_file:
                query = script_file.read()

        if "per_db" in q and q["per_db"]:
            # Have to run queries for all fetch dbs
            results = pg.per_db_query(query)
            for (dbname, result) in results.items():
                to_print = to_print + format_results(result, dbname=dbname,
                                                     measurement=measurement,
                                                     tagvalue=tagvalue)
        else:
            result = pg.query(query)
            to_print = to_print + format_results(result,
                                                 measurement=measurement,
                                                 tagvalue=tagvalue)

    print("\n".join(to_print))

def set_cwd():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("ERROR: Please pass the config file path as argument")
    set_cwd()
    with open(sys.argv[1]) as conf_file:
        CONF = toml.load(conf_file)["postgresql_custom"]
    if "address" in CONF:
        PG = PGQuerier(dsn=CONF["address"])
    else:
        PG = PGQuerier()
    while True:
        sys.stdin.readline()
        print_data(PG, CONF)
