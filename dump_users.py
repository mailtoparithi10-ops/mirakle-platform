
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mirakle.db')
if not os.path.exists(db_path):
    print("DB NOT FOUND in instance, checking root...")
    db_path = 'mirakle.db'

print(f"Checking DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email, role, password_hash FROM user")
    users = cursor.fetchall()
    
    with open("users_dump.txt", "w") as f:
        f.write(f"Total Users: {len(users)}\n")
        if not users:
            f.write("NO USERS FOUND.\n")
        for u in users:
            # truncate hash for readability
            p_hash = u[2][:20] + "..." if u[2] else "None"
            f.write(f"Email: {u[0]}, Role: {u[1]}, Hash: {p_hash}\n")
            
    conn.close()
    print("Done dumping users.")
except Exception as e:
    with open("users_dump.txt", "w") as f:
        f.write(f"ERROR: {e}")
    print(f"Error: {e}")
