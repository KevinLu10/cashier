# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'
import time
import os
import xlrd, xlwt, xlutils
from sql_utils import *
import utils as utils
from datetime import datetime


def get_data_in_detail(sql_conn,kwargs):
    '''
    获取需要在收纳页面显示的其他信息，包括客户信息，账号信息等
    :param sql_conn: 数据库连接
    :param kwargs: 用户信息
    :return: dict
    '''
    types = ['client', 'proof', 'paytype', 'account']
    data = {}
    for type in types:
        keys = ['%s_id' % type, '%s_name' % type]
        sql = get_s_sql(type, keys, {})
        r = sql_conn.execute(sql)
        data[type] = utils.sql_result(r, keys)
    # 获取用户信息
    access=kwargs.get('access')
    if 'admin' in access or 'common' in access:
        keys = ['username']
        sql = get_s_sql('user', keys, {})
        r = sql_conn.execute(sql)
        data['username'] = utils.sql_result(r, keys)
    else:data['username']=[{'username':kwargs.get('username')}]

    # 统计账户余额信息
    for account in data['account']:
        account['balance'] = get_balance(sql_conn, account['account_id'])
    return data


def get_balance(sql_conn, account_id):
    '''
    获取一个账号到当前时间的余额
    :param sql_conn: 数据库连接
    :param account_id: 账号id
    :return: int
    '''
    sql = get_s_sql('cashier', ['sum(actual_money)'], {'account_id': account_id}) + \
          ' and date < "%s"' % str(datetime.now())
    r = sql_conn.execute(sql, 1)
    return r[0] or 0


def currency_exchange(src, ex_from, ex_to, rate):
    '''
    货币转换
    :param src: float 需要转换的金额
    :param ex_from: str 转换前的币种
    :param ex_to: str 转换后的币种
    :param rate: dict 比率信息 {'ab':2,'dollar':3.2} 2代表1人民币=2澳币
    :return: 转换结果
    '''
    if not src:return src
    src=float(src)
    if ex_from == ex_to:
        return src
    rate.update({'rmb': 1})
    target = src / float(rate[ex_from]) * float(rate[ex_to])

    return '%.2f'%target

def exchage_data(data,kwargs,ex_from=''):
    rate={'ab':kwargs.get('currency_rate_rmb2ab',1),'dollar':kwargs.get('currency_rate_rmb2dollar')}
    ex_to=kwargs.get('currency')
    if ex_to=='no_exchange':
        return data

    def _exchange(data):
        ex_from=data['account_currency']
        keys=data.keys()

        for key in keys:
            if 'money' in key:
                data[key]=currency_exchange(data[key],ex_from,ex_to,rate)

    if isinstance(data,dict):
        _exchange(data)
    elif isinstance(data,list):
        for d in data:
            _exchange(d)
    else:
        data=currency_exchange(data,ex_from,ex_to,rate)
    return data

def input_xls(file_path,sql_conn,keys,username):
    '''
    导入xls文件的数据到数据库
    :param file_path: 导入的文件路径
    :param sql_conn: 数据库连接
    :param keys:  数据库列名
    :return:1
    '''
    from copy import copy
    keys=copy(keys)
    keys.remove('pay_user')
    r_file =xlrd.open_workbook(file_path)
    sheet0=r_file.sheets()[0]#通过索引顺序获取
    nrows = sheet0.nrows #获取行数
    if nrows<2:return 1
    #获取已有的数据
    data={} #data={'client':{'client_id':'client_name'}}
    types=['client', 'proof', 'paytype', 'account']
    for type in types:
        keys_ = [ '%s_name' % type,'%s_id' % type]
        sql = get_s_sql(type, keys_, {})
        r = sql_conn.execute(sql)
        data[type] = dict(r)
    for row_index in range(1,nrows):
        one_row={'pay_user':username}
        for i ,key in enumerate(keys):
            src=sheet0.cell(row_index,i).value

            if key=='date':
                one_row[key]=datetime(*xlrd.xldate_as_tuple(src,0)[0:3]).strftime('%Y-%m-%d')
            else:
                if isinstance(src,basestring):

                    one_row[key]=src
                else:one_row[key]=str(src)


        for type in types:
            if one_row['%s_id'%type] in data[type]:
                one_row['%s_id'%type]=data[type][one_row['%s_id'%type]]
            else:
                sql=get_i_sql(type,{ '%s_name' % type:one_row['%s_id'%type]})
                sql_conn.execute(sql)
                one_row['%s_id'%type]=sql_conn.last_id()
        sql=get_i_sql('cashier',one_row)

        sql_conn.execute(sql)
    sql_conn.commit()
    return 1




def output_xls(data, cashier_keys_2ch, keys, date1, date2):
    '''
    导出xls文件
    :param data: 数据
    :param cashier_keys_2ch: keys的英中转换
    :param keys: 排好序的key
    :param date1: 开始时间
    :param date2: 结束时间
    :return:xls文件的路径
    '''
    if not data:return ''
    file_name = 'cashier{0}.xls'.format(str(int(time.time())))
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'xls', file_name)
    w_file = xlwt.Workbook()
    sheet0 = w_file.add_sheet(u'出纳数据')
    for i, key in enumerate(keys):
        sheet0.write(0, i, cashier_keys_2ch[key].decode('utf-8'))
    for i, d in enumerate(data):
        for j, key in enumerate(keys):
            sheet0.write(i+1, j, d[key])
    w_file.save(path)
    return '/static/xls/{0}'.format(file_name)

