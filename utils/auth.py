# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'
from lib.bottle import request,redirect
from datetime import datetime,timedelta
import conf
from sql_conn import SqlConn
import sql_utils
import utils


def auth(access_required):
    '''
    认证用户是否有权限，装饰器
    :param access_required: 访问该uri需要的权限
    :return:
    '''
    def _auth(func):
        def __auth(*args,**kwargs):
            token=request.cookies.get('token')
            if  token:
                keys= ['username','date','access','former_show_col', 'future_show_col', 'currency',
                       'currency_rate_rmb2ab', 'currency_rate_rmb2dollar','last_pay_code']
                sql=sql_utils.get_s_sql('token,user',keys,{'token':token})+' and token.token_username=user.username'
                sql_conn=SqlConn()
                r=sql_conn.execute(sql)
                if  r :
                    params=utils.sql_result(r,keys)[0]
                    if access_required in params['access']:
                        if datetime.strptime(params['date'], "%Y-%m-%d %X") +timedelta(seconds=conf.LOGIN_DEALINE)>datetime.now():
                            return func(**params)
                    else:
                        return '权限不足'

            return  redirect('/login')
        return __auth
    return _auth
