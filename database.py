import sqlite3

def create_tables():
    conn = sqlite3.connect("usta_bot.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS workers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    service_type TEXT,
                    gender TEXT,
                    phone TEXT
                )""")
    conn.commit()
    conn.close()

def add_worker(name, service_type, gender, phone):
    conn = sqlite3.connect("usta_bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO workers (name, service_type, gender, phone) VALUES (?, ?, ?, ?)", 
              (name, service_type, gender, phone))
    conn.commit()
    conn.close()

def get_workers_by_service(service_type, gender):
    conn = sqlite3.connect("usta_bot.db")
    c = conn.cursor()
    c.execute("SELECT name, phone FROM workers WHERE service_type = ? AND gender = ?", 
              (service_type, gender))
    result = c.fetchall()
    conn.close()
    return result
