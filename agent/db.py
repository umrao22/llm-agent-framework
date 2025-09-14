import mysql.connector
from config import DB_CONFIG

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def db_get_product_by_id(product_id: int):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"ok": False, "error": f"No product with id {product_id}"}
    return {"ok": True, "product": row}

def db_search_products(query: str, limit: int = 5):
    limit = min(limit, 100)  # clamp value to schema rules
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    like = f"%{query}%"
    cur.execute(
        "SELECT * FROM products WHERE name LIKE %s OR description LIKE %s LIMIT %s",
        (like, like, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"ok": True, "results": rows}

def db_get_inventory(product_id: int):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, stock FROM products WHERE id = %s", (product_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"ok": False, "error": f"No product with id {product_id}"}
    return {"ok": True, "inventory": row}
