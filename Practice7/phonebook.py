import csv
import psycopg2
from connect import get_connection

def sync_db_to_csv(filename='contacts.csv'):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT username, phone_number FROM phonebook ORDER BY username ASC")
            rows = cur.fetchall()
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            cur.close()
            conn.close()
            print(f"--- {filename} updated from database ---")
        except Exception as e:
            print(f"Error syncing to CSV: {e}")

def import_csv(filename):
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 2: continue
                    cur.execute("""
                        INSERT INTO phonebook (username, phone_number) 
                        VALUES (%s, %s) 
                        ON CONFLICT (phone_number) DO NOTHING
                    """, (row[0], row[1]))
            conn.commit()
            cur.close()
            conn.close()
            print("--- CSV Import complete ---")
        except Exception as e:
            print(f"Error importing CSV: {e}")

def add_contact():
    name = input("Enter Name: ")
    phone = input("Enter Phone Number: ")
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO phonebook (username, phone_number) VALUES (%s, %s)", (name, phone))
            conn.commit()
            cur.close()
            conn.close()
            print("--- Contact added to Database ---")
            sync_db_to_csv() 
        except Exception as e:
            print(f"Error adding contact: {e}")

def update_contact():
    target_name = input("Enter the EXACT name of the contact to update: ")
    print("1. Update Name\n2. Update Phone")
    choice = input("Choice: ")
    
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        if choice == "1":
            new_name = input("Enter new name: ")
            cur.execute("UPDATE phonebook SET username = %s WHERE username = %s", (new_name, target_name))
        elif choice == "2":
            new_phone = input("Enter new phone: ")
            cur.execute("UPDATE phonebook SET phone_number = %s WHERE username = %s", (new_phone, target_name))
        
        conn.commit()
        cur.close()
        conn.close()
        print("--- Update complete ---")
        sync_db_to_csv() 

def search_contacts():
    print("Search by:\n1. Name (or part of name)\n2. Phone Prefix")
    choice = input("Choice: ")
    
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        if choice == "1":
            val = input("Enter name to search: ")
            cur.execute("SELECT * FROM phonebook WHERE username ILIKE %s", (f"%{val}%",))
        else:
            val = input("Enter phone prefix (e.g. 8707): ")
            cur.execute("SELECT * FROM phonebook WHERE phone_number LIKE %s", (f"{val}%",))
        
        results = cur.fetchall()
        print("\n--- Search Results ---")
        for row in results:
            print(f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
        cur.close()
        conn.close()

def delete_contact():
    val = input("Enter the Name or Phone Number to delete: ")
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM phonebook WHERE username = %s OR phone_number = %s", (val, val))
        conn.commit()
        cur.close()
        conn.close()
        print(f"--- Deleted record matching: {val} ---")
        sync_db_to_csv() 

def main_menu():
    while True:
        print("\n========================")
        print("    PHONEBOOK MENU      ")
        print("========================")
        print("1. Import from CSV")
        print("2. Add New Contact")
        print("3. Update Contact")
        print("4. Search/Filter")
        print("5. Delete Contact")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ")
        
        if choice == "1": import_csv('contacts.csv')
        elif choice == "2": add_contact()
        elif choice == "3": update_contact()
        elif choice == "4": search_contacts()
        elif choice == "5": delete_contact()
        elif choice == "6": 
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    sync_db_to_csv()  
    main_menu()