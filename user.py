from flask import current_app
from flask_login import UserMixin
import psycopg2
import os

conn = psycopg2.connect(os.environ.get("DATABASE_URL"), sslmode='require')

class User(UserMixin):
    def __init__(self, username, password, id, privelege_type):
        self.username = username
        self.password = password
        self.id = id
        self.privelege_type = privelege_type
        self.active = True
      

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    if row is not None:
        id = row[0]
        username = row[1]
        password = row[2]
        cur.execute("SELECT * FROM privilege WHERE id=%s", (id,))
        row = cur.fetchone()
        if row is not None:
            privelege_type = row[1]
        user = User(username, password, id, privelege_type) if password else None
        return user
    else:
        return 0