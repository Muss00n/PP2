import psycopg2
from connect import get_connection

def search_by_pattern(pattern):
    conn = get_connection()
    cur = conn.cursor()
    # Calling a FUNCTION uses SELECT
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def upsert_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    # Calling a PROCEDURE uses CALL
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("User processed.")

def get_paginated(limit, offset):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def delete_user(identifier):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_contact_by_id(%s)", (identifier,))
    conn.commit()
    cur.close()
    conn.close()
    print("Delete procedure executed.")

if __name__ == "__main__":
    # Example Tests:
    print("Testing Search:")
    search_by_pattern("8707")
    
    print("\nTesting Pagination (Limit 2, Offset 0):")
    get_paginated(2, 0)
    
    print("\nTesting Upsert:")
    upsert_user("Alibi", "87779990011")