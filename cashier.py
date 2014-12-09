# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'

from lib.bottle import *
import time
from copy import copy
import hashlib
import logging
import utils.utils as utils
from utils.sql_utils import *
from utils import cashier_utils
from utils.sql_conn import SqlConn
import random, string
from datetime import datetime

sql_conn = SqlConn()
user_keys = ['username', 'pwd', 'group']
cashier_keys = ['date', 'client_id', 'account_id', 'cashier_code'
    , 'paytype_id', 'pay_user', 'proof_id', 'payable_money', 'actual_money', 'money', 'remark','is_remind']

cashier_keys_2ch = {'date': '日期', 'client_name': '客户名称', 'account_name': '账户'
    , 'paytype': '方式', 'pay_user': '操作人员', 'proof_name': '凭证', 'payable_money': '应变动金额', 'actual_money': '实变动金额',
                    'money': '差额金额', 'remark': '备注', 'cashier_code': '操作编号', 'is_remind': '是否提醒'
}


def login():
    '''
    登陆
    '''
    username = request.params.get('username')
    pwd = request.params.get('pwd')
    keys = ['username', 'access']
    sql = get_s_sql('user,groups', keys,
                    {'username': username, 'pwd': hashlib.md5(pwd).hexdigest()}) + ' and groups.group_id==user.group_id'
    r = sql_conn.execute(sql)

    if not r:
        return template('login', msg='账号密码错误')
    params = utils.sql_result(r, keys)[0]
    token = ''.join(random.sample(string.ascii_letters + string.digits, 10)) + str(int(time.time()))
    params.update({'token': token, 'date': datetime.now().strftime("%Y-%m-%d %X")})
    params['token_username'] = params['username']
    del params['username']
    i_sql = get_i_sql('token', params)

    sql_conn.execute(i_sql)
    sql_conn.commit()
    response.set_cookie('token', token)
    return redirect('/s_cashier_list')


def logout():
    '''
    登出
    '''
    response.set_cookie('token', '')
    return redirect('/login')


def user_man(*args, **kwargs):
    '''
    用户管理页面
    '''
    sql = get_s_sql('groups', ['group_id', 'group_name'], {})
    r = sql_conn.execute(sql)
    if not r:
        return 'error'
    group = dict(r)
    return template('user_man', group=group)


def s_user(*args, **kwargs):
    '''
    搜索用户
    '''
    keys = ['username', 'pwd', 'group_name']
    sql = get_s_sql('user,groups', keys, {}) + ' where user.group_id=groups.group_id'
    r = sql_conn.execute(sql)
    data = utils.sql_result(r, keys)
    data = template('user_man_include', data=data)
    return {'retcode': 1, 'data': data}


def d_user(*args, **kwargs):
    '''
    删除用户
    '''
    username = request.params.get('username')
    sql = get_d_sql('user', {'username': username})
    sql_conn.execute(sql)
    return {'retcode': 1}


def i_user(*args, **kwargs):
    '''
    插入用户
    '''
    params = utils.get_params(['username', 'pwd', 'group_id'])
    params['pwd']=hashlib.md5(params['pwd']).hexdigest()
    sql = get_i_sql('user', params)
    sql_conn.execute(sql)
    return {'retcode': 1}


def i_cashier(*args, **kwargs):
    '''
    插入数据的页面
    '''
    data = cashier_utils.get_data_in_detail(sql_conn, kwargs)
    # 自动填写收款编号
    years = datetime.now().strftime('%Y')
    date = datetime.now().strftime('%Y%m%d')
    cashier_code={}
    for sub in ('SR','ZC'):
        sql = 'select cashier_code from cashier where date like "{0}%" and cashier_code like "{1}%" '.format(years,sub)

        r = sql_conn.execute(sql)

        if r:
            try:
                cashier_codes=[ x[0] for x in r if re.match('%s-\d{8}-\d{4}'%sub,x[0])]
                cashier_codes.sort(key=lambda x:int(x.split('-')[-1]))
                num = int(cashier_codes[-1].split('-')[-1]) + 1
            except:

                num = 0
            cashier_code[sub] = 'SR-{0}-{1:0>4}'.format(date, num)
        else:
            cashier_code[sub] = 'SR-{0}-{1:0>4}'.format(date, 0)


    return template('cashier_detail', data=data, cashier_code=cashier_code)


def i_cashier_post(*args, **kwargs):
    '''
    插入数据
    '''
    params = utils.get_params(cashier_keys)
    type = request.params.get('type')  # pay or get
    params['actual_money'] = abs(float(params['actual_money'])) if type == 'get' else -abs(
        float(params['actual_money']))

    def _insert(date):
        params['date'] = date
        sql = get_i_sql('cashier', params)
        sql_conn.execute(sql)

    days = request.params.get('days')
    future_date = request.params.get('future_date')

    if days and future_date:
        try:
            days = int(days)
            cur_date = datetime.strptime(params['date'], '%Y-%m-%d')
            futute_date = datetime.strptime(future_date, '%Y-%m-%d')
        except:
            return {'retcode': 0}
        while cur_date <= futute_date:
            _insert(cur_date.strftime('%Y-%m-%d'))
            cur_date += timedelta(days=days)
    else:
        _insert(params['date'])
    sql_conn.commit()
    return {'retcode': 1}


def u_cashier(*args, **kwargs):
    '''
    更新数据
    '''
    param = utils.get_params(cashier_keys )
    sql = get_u_sql('cashier', param,{'cashier_id':request.params.get('cashier_id')})
    sql_conn.execute(sql)
    return {'retcode': 1}


def s_cashier_detail(*args, **kwargs):
    '''
    获取一条收纳数据的明细
    '''
    param = utils.get_params(['cashier_id'])
    if 'admin' not in kwargs.get('access'):
        param['pay_user'] = kwargs.get('username')
    keys = copy(cashier_keys) + ['cashier_id', 'account_currency', 'cashier.account_id']
    keys.remove('account_id')

    sql = get_s_sql('cashier,account', keys, param) + ' and account.account_id=cashier.account_id'
    r = sql_conn.execute(sql)
    if not r: return '系统出错'
    cashier_data = utils.sql_result(r, keys)[0]
    cashier_data = cashier_utils.exchage_data(cashier_data, kwargs)
    data = cashier_utils.get_data_in_detail(sql_conn, kwargs)
    return template('cashier_detail', cashier_data=cashier_data, data=data, ctrl_type='update')


def s_cashier_list(*args, **kwargs):
    '''
    返回明细的页面
    '''
    former_show_col = kwargs.get('former_show_col')  # 帮用户选中的列

    return template('cashier_list', former_show_col=former_show_col)


def s_cashier_list_post(*args, **kwargs):
    '''
    返回明细的内容
    '''
    param = utils.get_params(['date1', 'date2'])
    is_output_xls = request.params.get('is_output_xls')  # 标记是否导出到xls
    user_cond = '' if 'admin' in kwargs.get('access') else 'pay_user="%s" and '% kwargs.get('username')
    #支出还是收入的筛选
    type=request.params.get('type')
    type_cond={'get':'actual_money>=0 and ','pay':' actual_money<=0 and '}[type] if type else ''
    keys = request.params.get('show_cols').split(';')
    cashier_keys_ = cashier_keys + ['client_name', 'account_name', 'proof_name', 'paytype_name']
    keys = filter(lambda x: x in keys, cashier_keys_)
    order_type='desc' if request.params.get('ctrl_typ')=='list' else ''
    def _get_sql(keys, index=None):
        limit_sql = ' limit {0},20'.format(index) if index != None else ''

        sql = get_s_sql('cashier,client,proof,account,paytype', keys, {}) + \
              " where {user_cond} {type_cond}  cashier.client_id=client.client_id and \
              cashier.proof_id=proof.proof_id and cashier.account_id=account.account_id and " \
              "cashier.paytype_id=paytype.paytype_id and date>='{date1}' and  date<= '{date2}'" \
              " order by date {order_type} {limit_sql}".\
                  format(limit_sql=limit_sql,order_type=order_type,user_cond=user_cond,
                         type_cond=type_cond,**param)
        return sql

    sql_index = utils.get_sql_index()
    total_num = 0
    if sql_index == 0 and not is_output_xls:
        # 计算数据的条数
        sql = _get_sql(['count(*)'])
        r = sql_conn.execute(sql, 1)
        total_num = r[0]

    key_ = keys + ['cashier_id', 'account_currency']
    sql = _get_sql(key_, None) if is_output_xls else _get_sql(key_, sql_index)

    r = sql_conn.execute(sql)
    data = utils.sql_result(r, keys + ['cashier_id', 'account_currency'])
    data = cashier_utils.exchage_data(data, kwargs)
    if is_output_xls:
        url = cashier_utils.output_xls(data, cashier_keys_2ch, keys, param['date1'], param['date2'])
        return {'retcode': 1, 'url': url}
    print keys
    return {'retcode': 1,
            'data': template('cashier_list_include', data=data, cashier_keys_2ch=cashier_keys_2ch, keys=keys),
            'total_num': total_num}


def cashier_future(**kwargs):
    '''
    返回未来收支的页面
    '''
    future_show_col = kwargs.get('future_show_col')  # 帮用户选中的列

    return template('cashier_future_list', former_show_col=future_show_col)


def d_cashier(*args, **kwargs):
    '''
    删除数据
    '''
    param = utils.get_params(['cashier_id'])
    sql = get_d_sql('cashier', param)
    sql_conn.execute(sql)
    sql_conn.commit()
    return {'retcode': 1}


def new_item(*args, **kwargs):
    '''
    新增类别
    '''
    item_type = request.params.get('item_type')
    item_name = request.params.get('item_name')
    sql = get_i_sql(item_type, {'%s_name' % item_type: item_name})
    sql_conn.execute(sql)
    sql_conn.commit()
    item_id = sql_conn.last_id()
    return {'retcode': 1, 'item_id': str(item_id)}


def new_account(*args, **kwargs):
    '''
    新增账户
    '''
    cd = utils.get_params(['account_name', 'account_desc', 'account_currency', 'account_about', 'account_label'])
    sql = get_i_sql('account', cd)
    sql_conn.execute(sql)
    sql_conn.commit()
    item_id = sql_conn.last_id()
    return {'retcode': 1, 'item_id': str(item_id)}


def report_ratio(*args, **kwargs):
    '''
    账户金额比例的饼状图
    '''
    keys = ['account_id', 'account_name', 'account_currency']
    sql = get_s_sql('account', keys, {})
    r = sql_conn.execute(sql)
    accounts = utils.sql_result(r, keys)
    for account in accounts:
        balance = cashier_utils.get_balance(sql_conn, account['account_id'])
        account['balance'] = cashier_utils.exchage_data(balance, kwargs, account['account_currency'])
    total_balance = float(sum([account['balance'] for account in accounts]))
    name_ratio = [[account['account_name'], float(account['balance']) / total_balance] for account in accounts]
    return {"retcode": 1, "data": name_ratio}


def report_tendency(*args, **kwargs):
    '''
    收支趋势图
    '''
    date1 = request.params.get('date1')
    date2 = request.params.get('date2')
    if date1 > date2: date1, date2 = date2, date1
    if not (date1 and date2): return {'retcode': 'invalid date'}
    cur_date = datetime.strptime(date1, '%Y-%m-%d')
    cur_years_month = [int(cur_date.strftime('%Y')), int(cur_date.strftime('%m'))]  # [2014,12]
    date2 = datetime.strptime(date2, '%Y-%m-%d')
    date2_years_month = [int(date2.strftime('%Y')), int(date2.strftime('%m'))]  # [2015,2]
    money_get = []
    money_pay = []
    months = []
    while cur_years_month <= date2_years_month:
        months.append('{0}-{1}'.format(*cur_years_month))
        print months
        for money, ctrl in ((money_get, '>'), (money_pay, '<')):
            sql = get_s_sql('cashier,account', ['actual_money', 'account_currency'], {}) + \
                  'where actual_money{1}0 and date >= "{0}-01" and date<="{0}-31" and cashier.account_id=' \
                  'account.account_id'.format('{0}-{1}'.format(*cur_years_month), ctrl)
            r = sql_conn.execute(sql)
            data = utils.sql_result(r, ['actual_money', 'account_currency'])
            data = cashier_utils.exchage_data(data, kwargs)
            total_money = sum([x['actual_money'] for x in data])
            money.append(abs(total_money) or 0)
        if cur_years_month[1] == 12:
            cur_years_month = (cur_years_month[0] + 1, 1)
        else:
            cur_years_month[1] += 1
    return {'retcode': 1, 'money_get': money_get, 'money_pay': money_pay, 'months': months}


def settings(*args, **kwargs):
    '''
    修改配置
    '''
    username = kwargs.get('username')
    params = utils.get_params(
        ['former_show_col', 'future_show_col', 'currency', 'currency_rate_rmb2ab', 'currency_rate_rmb2dollar'])
    pwd_old = request.params.get('pwd_old')
    pwd_new1 = request.params.get('pwd_new1')
    pwd_new2 = request.params.get('pwd_new2')
    if pwd_old and pwd_new1 and pwd_new2:
        if pwd_new2 != pwd_new1:
            return {'retcode': 0, 'msg': '两次新密码不相同'}
        if len(pwd_new1) > 20:
            return {'retcode': 0, 'msg': '密码长度不能大于20位'}
        sql = get_s_sql('user', ['*'], {'username': username, 'pwd': hashlib.md5(pwd_old).hexdigest()})
        r = sql_conn.execute(sql)
        if not r:
            return {'retcode': 0, 'msg': '原密码错误'}
        params['pwd'] = hashlib.md5(pwd_new1).hexdigest()

    sql = get_u_sql('user', params, {'username': username})
    sql_conn.execute(sql)
    sql_conn.commit()
    return {'retcode': 1}


def input_xls(*args, **kwargs):
    '''
    从xls导入数据
    '''
    file_path = 'static/xls/{0}.xls'.format(str(int(time.time())))
    request.files.get('input_xls').save(file_path)
    cashier_utils.input_xls(file_path, sql_conn, cashier_keys, kwargs.get('username'))
    return '导入成功'