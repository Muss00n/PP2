import csv
import json
import os
import psycopg2
from connect import get_connection

# ──────────────────────────────────────────────────────────────
# Helper: print a list of contact rows nicely
# ──────────────────────────────────────────────────────────────
def print_contacts(rows, headers=None):
    if not rows:
        print("  (no results)")
        return
    if headers:
        print("  " + " | ".join(str(h).ljust(18) for h in headers))
        print("  " + "-" * (21 * len(headers)))
    for row in rows:
        print("  " + " | ".join(str(v or "").ljust(18) for v in row))
    print()


# ══════════════════════════════════════════════════════════════
# 3.1  Schema init (run schema.sql + procedures.sql)
# ══════════════════════════════════════════════════════════════
def init_schema():
    base = os.path.dirname(os.path.abspath(__file__))
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        for fname in ("schema.sql", "procedures.sql"):
            path = os.path.join(base, fname)
            with open(path, "r", encoding="utf-8") as f:
                cur.execute(f.read())
            print(f"  ✓ {fname} executed")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")


# ══════════════════════════════════════════════════════════════
# 3.2  Advanced Console Search & Filter
# ══════════════════════════════════════════════════════════════

def filter_by_group():
    group = input("  Enter group name (Family/Work/Friend/Other): ").strip()
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT pb.contact_id, pb.username, pb.phone_number,
                   pb.email, pb.birthday, g.name
            FROM phonebook pb
            LEFT JOIN groups g ON g.id = pb.group_id
            WHERE g.name ILIKE %s
            ORDER BY pb.username
        """, (group,))
        rows = cur.fetchall()
        print_contacts(rows, ["ID", "Username", "Phone", "Email", "Birthday", "Group"])
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")


def search_by_email():
    pattern = input("  Enter email pattern (e.g. gmail): ").strip()
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT contact_id, username, phone_number, email, birthday
            FROM phonebook
            WHERE email ILIKE %s
            ORDER BY username
        """, (f"%{pattern}%",))
        rows = cur.fetchall()
        print_contacts(rows, ["ID", "Username", "Phone", "Email", "Birthday"])
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")


def sort_contacts():
    print("  Sort by:  1) name   2) birthday   3) date added (id)")
    choice = input("  Choice: ").strip()
    col = {"1": "username", "2": "birthday", "3": "contact_id"}.get(choice, "username")
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT pb.contact_id, pb.username, pb.phone_number,
                   pb.email, pb.birthday, g.name
            FROM phonebook pb
            LEFT JOIN groups g ON g.id = pb.group_id
            ORDER BY {col} NULLS LAST
        """)
        rows = cur.fetchall()
        print_contacts(rows, ["ID", "Username", "Phone", "Email", "Birthday", "Group"])
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")


def paginated_navigation():
    page_size = 5
    offset = 0
    conn = get_connection()
    if not conn:
        return
    while True:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (page_size, offset))
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            print(f"  Error: {e}")
            conn.close()
            return

        print_contacts(rows, ["ID", "Username", "Phone"])
        print(f"  Page {offset // page_size + 1}  |  Commands: next / prev / quit")
        cmd = input("  > ").strip().lower()

        if cmd == "next":
            if len(rows) == page_size:
                offset += page_size
            else:
                print("  Already on the last page.")
        elif cmd == "prev":
            if offset == 0:
                print("  Already on the first page.")
            else:
                offset -= page_size
        elif cmd == "quit":
            break
        else:
            print("  Unknown command.")
    conn.close()


# ══════════════════════════════════════════════════════════════
# 3.3  Import / Export
# ══════════════════════════════════════════════════════════════

def export_to_json():
    path = input("  Output file name (default: contacts_export.json): ").strip()
    if not path:
        path = "contacts_export.json"
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT pb.contact_id, pb.username, pb.phone_number,
                   pb.email, pb.birthday::text, g.name AS group_name
            FROM phonebook pb
            LEFT JOIN groups g ON g.id = pb.group_id
            ORDER BY pb.username
        """)
        rows = cur.fetchall()
        data = []
        for row in rows:
            cid, username, phone, email, birthday, group_name = row
            # fetch extra phones
            cur2 = conn.cursor()
            cur2.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
            extra_phones = [{"phone": r[0], "type": r[1]} for r in cur2.fetchall()]
            cur2.close()
            data.append({
                "contact_id":   cid,
                "username":     username,
                "phone_number": phone,
                "email":        email,
                "birthday":     birthday,
                "group":        group_name,
                "extra_phones": extra_phones
            })
        cur.close()
        conn.close()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Exported {len(data)} contacts to {path}")
    except Exception as e:
        print(f"  Error: {e}")


def import_from_json():
    path = input("  JSON file path: ").strip()
    if not os.path.isfile(path):
        print("  File not found.")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        for rec in data:
            username = (rec.get("username") or "").strip()
            if not username:
                continue
            # Check duplicate
            cur.execute("SELECT contact_id FROM phonebook WHERE username = %s", (username,))
            existing = cur.fetchone()
            if existing:
                action = input(f'  "{username}" already exists. [s]kip / [o]verwrite? ').strip().lower()
                if action == "o":
                    cur.execute("""
                        UPDATE phonebook
                        SET phone_number=%s, email=%s, birthday=%s
                        WHERE username=%s
                    """, (rec.get("phone_number"), rec.get("email"),
                          rec.get("birthday"), username))
                continue
            # Insert
            # Ensure group
            group_id = None
            if rec.get("group"):
                cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (rec["group"],))
                g = cur.fetchone()
                if not g:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (rec["group"],))
                    g = cur.fetchone()
                group_id = g[0]
            cur.execute("""
                INSERT INTO phonebook (username, phone_number, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING contact_id
            """, (username, rec.get("phone_number"), rec.get("email"),
                  rec.get("birthday"), group_id))
            cid = cur.fetchone()[0]
            for ph in (rec.get("extra_phones") or []):
                cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                            (cid, ph.get("phone"), ph.get("type", "mobile")))
        conn.commit()
        cur.close()
        conn.close()
        print("  ✓ Import complete.")
    except Exception as e:
        print(f"  Error: {e}")


def import_from_csv():
    path = input("  CSV file path (default: contacts.csv): ").strip()
    if not path:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.csv")
    if not os.path.isfile(path):
        print("  File not found.")
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        imported = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = (row.get("username") or "").strip()
                phone    = (row.get("phone_number") or "").strip()
                email    = (row.get("email") or "").strip() or None
                birthday = (row.get("birthday") or "").strip() or None
                group    = (row.get("group") or "Other").strip()
                phone2   = (row.get("phone2") or "").strip() or None
                ptype2   = (row.get("phone2_type") or "mobile").strip()
                if not username:
                    continue
                # Ensure group
                cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group,))
                g = cur.fetchone()
                if not g:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group,))
                    g = cur.fetchone()
                group_id = g[0]
                # Upsert
                cur.execute("SELECT contact_id FROM phonebook WHERE username = %s", (username,))
                existing = cur.fetchone()
                if existing:
                    cid = existing[0]
                    cur.execute("""
                        UPDATE phonebook SET phone_number=%s, email=%s, birthday=%s, group_id=%s
                        WHERE contact_id=%s
                    """, (phone, email, birthday, group_id, cid))
                else:
                    cur.execute("""
                        INSERT INTO phonebook (username, phone_number, email, birthday, group_id)
                        VALUES (%s,%s,%s,%s,%s) RETURNING contact_id
                    """, (username, phone, email, birthday, group_id))
                    cid = cur.fetchone()[0]
                # Extra phone
                if phone2:
                    cur.execute("""
                        INSERT INTO phones (contact_id, phone, type)
                        VALUES (%s,%s,%s) ON CONFLICT DO NOTHING
                    """, (cid, phone2, ptype2))
                imported += 1
        conn.commit()
        cur.close()
        conn.close()
        print(f"  ✓ Imported {imported} rows from CSV.")
    except Exception as e:
        print(f"  Error: {e}")


# ══════════════════════════════════════════════════════════════
# 3.4  New Stored Procedure wrappers
# ══════════════════════════════════════════════════════════════

def search_pattern():
    pattern = input("  Search (name / phone / email): ").strip()
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()
        print_contacts(rows, ["ID", "Username", "Phone", "Email", "Birthday", "Group", "Extra Phone", "Type"])
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")


def add_phone_to_contact():
    name  = input("  Contact username: ").strip()
    phone = input("  New phone number: ").strip()
    ptype = input("  Type (home/work/mobile) [mobile]: ").strip() or "mobile"
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        cur.close()
        conn.close()
        print(f"  ✓ Phone added to {name}")
    except Exception as e:
        print(f"  Error: {e}")


def move_contact_to_group():
    name  = input("  Contact username: ").strip()
    group = input("  Group name: ").strip()
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        cur.close()
        conn.close()
        print(f"  ✓ {name} moved to '{group}'")
    except Exception as e:
        print(f"  Error: {e}")


def add_contact():
    username = input("  Username: ").strip()
    phone    = input("  Phone number: ").strip()
    email    = input("  Email (optional): ").strip() or None
    birthday = input("  Birthday YYYY-MM-DD (optional): ").strip() or None
    group    = input("  Group (Family/Work/Friend/Other) [Other]: ").strip() or "Other"
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group,))
        g = cur.fetchone()
        if not g:
            cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group,))
            g = cur.fetchone()
        cur.execute("""
            INSERT INTO phonebook (username, phone_number, email, birthday, group_id)
            VALUES (%s,%s,%s,%s,%s)
        """, (username, phone, email, birthday, g[0]))
        conn.commit()
        cur.close()
        conn.close()
        print(f"  ✓ Contact '{username}' added.")
    except Exception as e:
        print(f"  Error: {e}")


def delete_contact():
    val = input("  Enter username OR phone number to delete: ").strip()
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL delete_contact_by_val(%s)", (val,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"  ✓ Deleted: {val}")
    except Exception as e:
        print(f"  Error: {e}")


def bulk_insert():
    print("  Enter names and phones one by one. Type 'done' when finished.")
    names, phones = [], []
    while True:
        name = input("  Name (or 'done'): ").strip()
        if name.lower() == "done":
            break
        phone = input("  Phone (11 digits): ").strip()
        names.append(name)
        phones.append(phone)
    if not names:
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL bulk_insert_contacts(%s::text[], %s::text[])", (names, phones))
        conn.commit()
        cur.close()
        conn.close()
        print(f"  ✓ Bulk insert complete for {len(names)} entries.")
    except Exception as e:
        print(f"  Error: {e}")


# ══════════════════════════════════════════════════════════════
# Main Menu
# ══════════════════════════════════════════════════════════════

def main_menu():
    while True:
        print("""
======================== TSIS1 PHONEBOOK ========================
  Setup
    1. Init schema & procedures (run first!)
-----------------------------------------------------------------
  Search & Filter  (3.2)
    2. Search by pattern (name / phone / email)
    3. Filter by group
    4. Search by email pattern
    5. Sort all contacts
    6. Paginated navigation (next / prev / quit)
-----------------------------------------------------------------
  Import / Export  (3.3)
    7. Import from CSV
    8. Import from JSON
    9. Export to JSON
-----------------------------------------------------------------
  Manage Contacts
   10. Add contact
   11. Add extra phone to contact
   12. Move contact to group
   13. Bulk insert (with validation)
   14. Delete contact (by name or phone)
-----------------------------------------------------------------
    0. Exit
==================================================================""")
        choice = input("  Select option: ").strip()
        actions = {
            "1":  init_schema,
            "2":  search_pattern,
            "3":  filter_by_group,
            "4":  search_by_email,
            "5":  sort_contacts,
            "6":  paginated_navigation,
            "7":  import_from_csv,
            "8":  import_from_json,
            "9":  export_to_json,
            "10": add_contact,
            "11": add_phone_to_contact,
            "12": move_contact_to_group,
            "13": bulk_insert,
            "14": delete_contact,
        }
        if choice == "0":
            print("  Bye!")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("  Invalid option, try again.")


if __name__ == "__main__":
    main_menu()
