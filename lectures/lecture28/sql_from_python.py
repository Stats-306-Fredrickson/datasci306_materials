"""
sql_from_python.py
==================================================================
DATASCI 306, Lecture 28 companion -- the value of learning SQL.

In the lecture we ran SQL from R with DBI::dbGetQuery(con, "..."). The
*SQL itself* is not an R thing -- it is the database's language, and it
transfers to any host language. Here is the SAME SQL, run from Python
with nothing but the standard library (the `sqlite3` and `csv` modules).

Run it yourself:

    python3 sql_from_python.py

It loads mpg.csv into an in-memory SQLite database and runs queries that
are character-for-character the ones from the R lecture.
==================================================================
"""

import csv
import sqlite3


def load_mpg(con):
    """Read mpg.csv and copy it into the database as a table named `mpg`.

    This is Python's equivalent of R's dbWriteTable(con, "mpg", mpg).
    """
    with open("mpg.csv", newline="") as f:
        rows = list(csv.DictReader(f))

    # Give numeric columns real types so SQLite stores numbers (not text);
    # otherwise WHERE year = 2008 would never match the string "2008".
    schema = {
        "manufacturer": "TEXT", "model": "TEXT", "displ": "REAL",
        "year": "INTEGER", "cyl": "INTEGER", "trans": "TEXT", "drv": "TEXT",
        "cty": "INTEGER", "hwy": "INTEGER", "fl": "TEXT", "class": "TEXT",
    }
    cols = list(schema)
    con.execute(f"CREATE TABLE mpg ({', '.join(f'{c} {t}' for c, t in schema.items())})")
    con.executemany(
        f"INSERT INTO mpg VALUES ({', '.join(':' + c for c in cols)})",
        rows,
    )


def run(con, label, query):
    """Run one SQL query and print the rows, with a header."""
    print(f"\n# {label}")
    print(query.strip())
    print("-> result:")
    cur = con.execute(query)
    headers = [d[0] for d in cur.description]
    print("   " + " | ".join(headers))
    for row in cur.fetchall():
        print("   " + " | ".join(str(v) for v in row))


def main():
    # open an in-memory database and load the data
    con = sqlite3.connect(":memory:")
    load_mpg(con)

    # --- the SAME SQL strings as the R lecture -------------------

    run(con, "Average highway mileage by manufacturer (2008)", """
        SELECT manufacturer, AVG(hwy) AS mean_hwy
        FROM mpg
        WHERE year = 2008
        GROUP BY manufacturer
        ORDER BY mean_hwy DESC
        LIMIT 5
    """)

    run(con, "Classes with more than 30 cars (GROUP BY + HAVING)", """
        SELECT class, COUNT(*) AS n, AVG(hwy) AS mean_hwy
        FROM mpg
        GROUP BY class
        HAVING n > 30
    """)

    con.close()


# In the real world you would usually use pandas, which hands the SAME
# SQL string to the database and gives you back a DataFrame in one line:
#
#     import pandas as pd, sqlite3
#     con = sqlite3.connect(":memory:")
#     pd.read_csv("mpg.csv").to_sql("mpg", con, index=False)
#     pd.read_sql("SELECT manufacturer, AVG(hwy) AS mean_hwy "
#                 "FROM mpg GROUP BY manufacturer", con)
#
# Different language, different data structure -- identical SQL.


if __name__ == "__main__":
    main()
