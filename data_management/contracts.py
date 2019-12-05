import sqlite3
import os
from datetime import datetime
from tinydb import TinyDB, Query


DB_PATH = 'data_management/contracts.db'


def init_database():
    # backup old database
    if os.path.isfile(DB_PATH):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
        new_name = DB_PATH.split('.')[0] + '_backup_' + timestamp + '.db'
        os.rename(DB_PATH, new_name)

    # create new database
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE contracts (
        symbol text, 
        name text, 
        currency text, 
        exchange text, 
        status integer,
        status_text text)''')
    conn.commit()
    conn.close()


def create_contract(symbol, name, currency, exchange, status=0, \
    status_text='new contract'):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""INSERT INTO contracts VALUES (?, ?, ?,
        ?, ?, ?)""", (symbol, name, currency, exchange, status, status_text))

    conn.commit()
    conn.close()


def get_contracts(symbol='*', name='*', currency='*', exchange='*', \
    status='*', status_text='*'):
    """
    returns list of tuples
    """
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = 'SELECT * FROM contracts'

    filters = {}
    if symbol != '*': filters.update({'symbol': symbol})
    if name != '*': filters.update({'name': name})
    if currency != '*': filters.update({'currency': currency})
    if exchange != '*': filters.update({'exchange': exchange})
    if status != '*': filters.update({'status': status})
    if status_text != '*': filters.update({'status_text': status_text})

    if len(filters) > 0:
        query += ' WHERE '
    
    for key, value in filters.items():
        query += (key + " = '" + value + "' and ")

    if len(filters) > 0:
        query = query[:-5]

    cur.execute(query)
    result = cur.fetchall()

    conn.commit()
    conn.close()

    return result


def update_contract():
    pass


def delete_contracts():
    pass


def import_from_tinydb():
    TINY_DB_PATH = 'data_management/contracts_db.json'
    
    init_database()

    tiny_contracts_db = TinyDB(TINY_DB_PATH)
    result = tiny_contracts_db.all()
    tiny_contracts_db.close()

    for contract in result:
        create_contract(
            symbol=contract['Symbol'],
            name=contract['Name'],
            currency=contract['Currency'],
            exchange=contract['Exchange'],
            status=0,
            status_text=contract['Status'])


# init_database()
# create_contract('test', 'This is ma name', 'USD', 'TOY_X')
# result = get_contracts(symbol = 'BOL')
# import_from_tinydb()