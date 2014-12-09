# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'

from utils.sql_conn import SqlConn

'''
初始化数据库
'''
sqls = [
    '''
CREATE TABLE `user` (
 `username` char(50) primary key  ,
  `pwd` char(50) ,
  `group_id` int(6),
  currency char(10),
former_show_col  char(100),
future_show_col  char(100),
currency_rate_rmb2ab float(5),
currency_rate_rmb2dollar float(5),
last_pay_code char(50)
)
''',
    '''
    CREATE TABLE `groups` (
      `group_id` INTEGER primary key autoincrement,
      `group_name` char(20)   ,
     `access` text
    )
    ''',
    '''
    CREATE TABLE `client` (
      `client_id` INTEGER primary key autoincrement,
     `client_name` char(20)

    )
    ''',
    '''
    CREATE TABLE `proof` (
      `proof_id` INTEGER primary key autoincrement,
     `proof_name` char(20)

    )
    ''',
    '''
    CREATE TABLE `paytype` (
      `paytype_id` INTEGER primary key autoincrement,
     `paytype_name` char(20)

    )
    ''',
    '''
    CREATE TABLE `account` (
      `account_id` INTEGER primary key autoincrement,
     `account_name` char(20)   ,
     `account_desc` text  ,
      `balance` int(10),
      account_currency char(10),
      account_about char(10),
      account_label char(20)
    )
    ''',

    '''
    CREATE TABLE `cashier` (
      `cashier_id` INTEGER primary key autoincrement,
      `cashier_code` char(50) ,
     `date` datetime ,
      `client_id` int(10),
      `account_id`  int(6) ,
     `paytype_id`  char(10) ,
     `pay_user`  char(20) ,
     `proof_id` char(20) ,
     `payable_money`  float(6) ,
     `actual_money`  float(6) ,
     `money`  float(6),
     remark char(200),
     is_remind char(2)
    )
    ''',
    '''
    CREATE TABLE `token` (
      `token` char(10) primary key,
     `date` datetime   ,
      `token_username` char(20) ,
     `access` text  char(200)

    )
    '''
    , '''
insert into groups(group_name,access) values('超级用户','admin;common;limit')
'''
    , '''
insert into groups(group_name,access) values('普通用户','common;limit')
'''
    , '''
insert into groups(group_name,access) values('限制用户','limit')
''', '''
insert into user(username,pwd,group_id) values('admin','21232f297a57a5a743894a0e4a801fc3',1)
'''
]
import traceback


def main():
    sql_conn = SqlConn()
    for sql in sqls:
        try:
            print sql_conn.execute(sql)
        except:
            print traceback.print_exc()
    sql_conn.close(1)


if __name__ == '__main__':
    main()