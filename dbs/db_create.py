import sqlite3
import json

json_data_path = '../data/data.json'
quotes_data_path = '../data/quotes.json'

with open(json_data_path, 'r') as f:
    data = json.loads(f.read())
with open(quotes_data_path, 'r') as f:
    quotes = json.loads(f.read())

db = sqlite3.connect('db.sqlite')
cursor = db.cursor()

cursor.execute('Create Table if not exists Channels (name TEXT, id INTEGER PRIMARY KEY, role INTEGER, last_message INTEGER)')
cursor.execute('Create Table if not exists Variables (name TEXT PRIMARY KEY, val INTEGER)')
cursor.execute('Create Table if not exists Quotes (name TEXT, val TEXT, PRIMARY KEY (name, val))')

try:
    for channel in data['channels']:
        id = data['channels'][channel]['id']
        role = data['channels'][channel]['role']
        last_message = data['channels'][channel]['last_message']
        cursor.execute('insert into Channels values(?,?,?,?)', (channel, id, role, last_message))
except Exception as e:
    print(e)

try:
    for k in data:
        if k.startswith('v'):
            cursor.execute('insert into Variables values(?,?)', (k[1:], data[k]))
            print(k[1:])
except Exception as e:
    print(e)

try:
    for q in quotes:
        for qq in quotes[q]:
            cursor.execute('insert into Quotes values(?,?)', (q, qq))
except Exception as e:
    print(e)

db.commit()
db.close()