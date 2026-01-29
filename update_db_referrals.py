import sqlite3

def add_columns():
    conn = sqlite3.connect('mirakle.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE referrals ADD COLUMN token VARCHAR(100)")
        print("Column 'token' added successfully.")
    except sqlite3.OperationalError:
        print("Column 'token' already exists or other error.")
        
    try:
        cursor.execute("ALTER TABLE referrals ADD COLUMN is_link_referral BOOLEAN DEFAULT 0")
        print("Column 'is_link_referral' added successfully.")
    except sqlite3.OperationalError:
        print("Column 'is_link_referral' already exists or other error.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_columns()
