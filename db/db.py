import sqlite3
import datetime
import random
import os


NAMES = {
    0: 'Ilnar',
    1: 'Fedya',
    2: 'Gleb',
    3: 'Kostya',
    4: 'Leonid',
}


def init_db():
    with sqlite3.connect('sqlite3.db') as con:
        cur = con.cursor()

        cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                phone_number VARCHAR,
                datetime DATE
                );
        ''')

        for i in range(10):
            name = NAMES[random.randint(0, 4)]
            phone_str = ''.join([str(random.randint(0, 9)) for _ in range(11)])
            date_time = datetime.datetime.now()

            query = f"INSERT INTO users (name, phone_number, datetime) "\
                    f"VALUES ('{name}','{phone_str}','{date_time}')"
            cur.execute(query)

        con.commit()


def test_select():
    with sqlite3.connect('sqlite3.db') as con:

        query = """
            SELECT * from users
        """

        res = con.execute(query)

        for i in res:
            print(i)


if __name__ == '__main__':
    path_to_db = os.path.join(os.getcwd(), 'sqlite3.db')
    if not os.path.exists(path_to_db):
        print('DB initializing')
        init_db()
    else:
        print('DB exists')
