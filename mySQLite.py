import sqlite3


class SQLClass:

    server_name = 'server.db'
    db = None
    sql = None

    def __init__(self):
        self.db = sqlite3.connect(self.server_name)
        self.sql = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.sql.execute("""CREATE TABLE IF NOT EXISTS pizza_table (
        name TEXT,
        type INT,
        price INT
        )""")
        self.db.commit()

    def add_object(self, comp):
        self.sql.execute("SELECT name From pizza_table")
        self.sql.execute("INSERT INTO pizza_table VALUES "
                         "(?, ?, ?)", comp)
        self.db.commit()

    def print_table(self):  # вспомогательная функция
        self.sql.execute("SELECT * FROM pizza_table")
        values = self.sql.fetchall()
        for value in values:
            print(value)

    def remove_objects(self):
        self.sql.execute("DELETE From pizza_table")
