__author__ = 'lujianxing'
import sqlite3
import conf
import logging
class SqlConn():
    def __init__(self):
        self.conn= sqlite3.connect(conf.DB_PATH)
        self.cur=self.conn.cursor()

    def cur(self):
        return self.cur()
    def commit(self):
        self.conn.commit()
    def execute(self,sql,fetchone=0):
        if sql.split()[0].strip() in ('insert','delete','update'):
            logging.info(sql)
        print sql
        self.cur.execute(sql)
        return self.cur.fetchone() if fetchone else self.cur.fetchall()
    def last_id(self):
        sql='SELECT  last_insert_rowid()'
        return self.execute(sql,1)[0]
    def close(self,is_commit):
        if is_commit:
            self.commit()
        self.cur.close()
        self.conn.close()
