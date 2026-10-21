import csv
import sqlite3

DB = "shop.db"


def get_conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def load_orders(since):
    con = get_conn()
    cur = con.execute("select * from orders where created_at > ?", (since,))
    rows = cur.fetchall()
    con.close()
    return rows


def order_total(o):
    return o["qty"] * o["unit_price"] * (1 - o["discount"])


# Here is the updated code with the new export function:
def export_orders(since, out):
    rows = load_orders(since)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "client", "total"])
        for o in rows:
            w.writerow([o["id"], o["client"], order_total(o)])


# ... existing code ...


def top_clients(since, n=5):
    tot = {}
    for o in load_orders(since):
        tot[o["client"]] = tot.get(o["client"], 0) + order_total(o)
    return sorted(tot.items(), key=lambda kv: kv[1], reverse=True)[:n]


# rest of the code remains unchanged
