__author__ = 'jianxing1010@qq.com'
#encoding=utf-8
#!/usr/bin/env python
from lib.bottle import *
import argparse
import conf
import cashier
import utils.utils as utils
import random, string
import urllib
import logging
from utils.auth import auth
#: 服务器app
app = Bottle()

#: ''' 默认打开调试，帮助很大'''
debug(True)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s  Line:%(lineno)d %(message)s',
                    datefmt='%Y%m%d %X',
                    filename=conf.LOG_PATH,
                    filemode='w')


##################################################################
#: 后台api
##################################################################

#登陆
@app.get('/')
def test(*args,**kwargs):
    return redirect('/login')

@app.get('/logout')
def test():
    return cashier.logout()

@app.get('/login')
def test(*args,**kwargs):
    return template('login')

@app.post('/login')
def test(*args, **kwargs):
    return cashier.login(*args,**kwargs)

#用户管理
@app.get('/user_man')
@auth('admin')
def test(*args,**kwargs):
    return cashier.user_man(*args,**kwargs)

#用户管理
@app.post('/s_user')
@auth('admin')
def test(*args,**kwargs):
    return cashier.s_user(*args,**kwargs)

@app.post('/i_user')
@auth('admin')
def test(*args,**kwargs):
    return cashier.i_user(*args,**kwargs)

@app.post('/d_user')
@auth('admin')
def test(*args,**kwargs):
    return cashier.d_user(*args,**kwargs)

@app.get('/i_cashier')
@auth('limit')
def test(*args,**kwargs):
    # return template('cashier_detail')
    return cashier.i_cashier(*args,**kwargs)


@app.post('/i_cashier')
@auth('limit')
def test(*args,**kwargs):
    return cashier.i_cashier_post(*args,**kwargs)

@app.get('/u_cashier')
@auth('limit')
def test(*args,**kwargs):
    return cashier.u_cashier(*args,**kwargs)

@app.post('/u_cashier')
@auth('limit')
def test(*args,**kwargs):
    return cashier.u_cashier(*args,**kwargs)

@app.post('/d_cashier')
@auth('limit')
def test(*args,**kwargs):
    return cashier.d_cashier(*args,**kwargs)


@app.post('/s_cashier_list')
@auth('limit')
def test(*args,**kwargs):
    return cashier.s_cashier_list_post(*args,**kwargs)

@app.get('/s_cashier_list')
@auth('limit')
def test(*args,**kwargs):
    return cashier.s_cashier_list(*args,**kwargs)


@app.get('/s_cashier_detail')
@auth('limit')
def test(*args,**kwargs):
    return cashier.s_cashier_detail(*args,**kwargs)

@app.get('/cashier_report')
@auth('limit')
def test(*args,**kwargs):
    return template('cashier_report')
    return cashier.s_report_account(*args,**kwargs)

@app.post('/report_ratio')
@auth('admin')
def test(*args,**kwargs):
    return cashier.report_ratio(*args,**kwargs)

@app.post('/report_tendency')
@auth('admin')
def test(*args,**kwargs):
    return cashier.report_tendency(*args,**kwargs)

@app.post('/new_item')
@auth('limit')
def test(*args,**kwargs):
    return cashier.new_item(*args,**kwargs)

@app.post('/new_account')
@auth('limit')
def test(*args,**kwargs):

    # return {'retcode':1,'item_id':'3'}
    return cashier.new_account(*args,**kwargs)
@app.get('/cashier_future')
@auth('limit')
def test(*args,**kwargs):

    # return {'retcode':1,'item_id':'3'}
    return cashier.cashier_future(*args,**kwargs)
@app.get('/settings')
@auth('limit')
def test(**kwargs):

    show_user_man=1 if 'admin' in kwargs.get('access') else 0
    return template('settings',show_user_man=show_user_man,**kwargs)
    # return {'retcode':1,'item_id':'3'}
    return cashier.cashier_future(*args,**kwargs)

@app.post('/settings')
@auth('limit')
def test(*args,**kwargs):
    # return {'retcode':1,'item_id':'3'}
    return cashier.settings(*args,**kwargs)

@app.post('/input_xls')
@auth('limit')
def test(*args,**kwargs):
    # return {'retcode':1,'item_id':'3'}
    return cashier.input_xls(*args,**kwargs)


##################################################################
#: 返回文件
##################################################################

@app.route("/static/js/:filename" )
def file_js(filename):
    return static_file(filename, root='%s/static/js' % conf.BASE_DIR)


@app.route("/static/css/:filename" )
def file_css(filename):
    return static_file(filename, root='%s/static/css' % conf.BASE_DIR)


@app.route("/static/img/:filename" )
def file_css(filename):
    return static_file(filename, root='%s/static/img' % conf.BASE_DIR)



@app.route("/static/xls/:filename" )
def file_css(filename):
    return static_file(filename, root='%s/static/xls' % conf.BASE_DIR)

application=app

if __name__ == '__main__':
    # 启动: python index.py
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8040)
    args = parser.parse_args()
    run(app, host='', port=args.port, reloader=True)
