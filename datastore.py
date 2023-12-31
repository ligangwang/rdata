import os.path
import sqlite3
import contextlib
from datetime import date

file_path = f'./data/rts-{date.today()}.db'

def execute(f):
    def _execute(sqls, data_list):
        global file_path
        with contextlib.closing(sqlite3.connect(file_path)) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cur:
                    return f(cur, sqls, data_list)
    return _execute

@execute
def _execute_sqls(cur, sqls, data_list):
    for sql in sqls:
        cur.execute(sql)

@execute
def _execute_many(cur, sql, data_list):
    results = []
    for data in data_list:
        row = cur.execute(sql, data).fetchone()
        results.append(row[0] if row else None)
    return results

@execute
def _query(cur, sql, data):
    cur.execute(sql, data)
    return cur.fetchall()

def create_db():
    _execute_sqls([
    """
CREATE TABLE msg_in (source char(4), timestamp datetime DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')), message varchar(10))
""", 
    """
CREATE TABLE msg_out (timestamp datetime DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')), message varchar(10))
""",
    """
CREATE TABLE msg_latest (source char(4), timestamp datetime DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')), message varchar(10))
"""], None)

def init_db():
    global file_path
    if not os.path.exists(file_path):
        create_db()

def save_in_messages(source, messages):
    data = [(source, msg) for msg in messages]
    _execute_many("INSERT INTO msg_in (source, message) VALUES (?, ?)", data)

def save_latest_messages(source, messages):
    data = [(source, msg) for msg in messages]
    _execute_many("INSERT INTO msg_latest (source, message) VALUES (?, ?)", data)

def update_latest_messages(messages):
    data = [(msg, msg['oid']) for msg in messages]
    _execute_many("UPDATE msg_latest timestamp = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'), messaeg = ? WHERE oid = ?", data)

def get_in_messages():
    return _query("SELECT STRFTIME('%Y-%m-%d %H:%M:%f', timestamp) AS timestamp, message FROM msg_in", ())

def get_latest_messages():
    return _query("SELECT STRFTIME('%Y-%m-%d %H:%M:%f', timestamp) AS timestamp, message FROM msg_latest", ())


if __name__ == '__main__':
    init_db()
    #save_in_messages('test', ['msg1', 'msg2',  'msg3'])
    # save_latest_messages('test', ['1', '2', '3'])
    # update_latest_messages(['1', '2', '3'])
    print(get_in_messages())
    print(get_latest_messages())