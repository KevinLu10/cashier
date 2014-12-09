# encoding=utf-8
__author__ = 'lujianxing'

import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname((abspath(__file__)))))
from datetime import datetime, timedelta

from utils.sql_utils import *
from utils.sql_conn import *
from cashier import cashier_keys
from utils import utils

'''
检查X天后的未来收支,并发送信息
'''

pre_day = 3  # 提前多少天发送短信


def send_msg(data):
    '''
    发送信息
    :param data:数据 例子：[{'proof_id': u'1', 'account_id': 1, 'pay_user': u'admin', 'is_remind': u'1',
     'money': 0.0, 'remark': u'', 'paytype_id': u'1', 'cashier_code': u'SR-20141110-0004',
     'payable_money': 1000.0, 'client_id': 1, 'date': u'2014-11-13', 'actual_money': 1000.0}]
    :return:
    '''
    print data


def main():
    date_str = (datetime.now() + timedelta(days=pre_day)).strftime('%Y-%m-%d')
    sql = get_s_sql('cashier', cashier_keys, {'date': date_str, 'is_remind': 'Y'})
    sql_conn = SqlConn()
    r = sql_conn.execute(sql)
    if r:
        data = utils.sql_result(r, cashier_keys)
        send_msg(data)


if __name__ == '__main__':
    main()
