import sqlite3
from random import choice

db = sqlite3.connect('dbs/db.sqlite')
cursor = db.cursor()

def db_get_value(name):
    cursor.execute("SELECT val from Variables WHERE name = ?", (name,))
    return cursor.fetchone()[0]

def db_channels():
    cursor.execute('SELECT * from Channels')
    rows = cursor.fetchall()
    channels = {}
    for r in rows:
        channels[r[0]] = {
            'id' : r[1],
            'role': r[2]
        }
    return channels

def db_set_last_message(channel, message):
    cursor.execute('UPDATE Channels SET last_message = ? WHERE name = ?', (message, channel))
    db.commit()

def db_get_last_message(channel):
    cursor.execute('SELECT last_message from Channels WHERE name = ?', (channel,))
    try:
        return cursor.fetchone()[0]
    except:
        return -1

def db_get_quotes(name):
    cursor.execute('SELECT val from Quotes WHERE name = ?', (name,))
    return choice(cursor.fetchall())[0]
