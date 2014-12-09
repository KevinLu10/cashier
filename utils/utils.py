__author__ = 'jianxing1010@qq.com'
# encoding=utf8
import sys
sys.path.append('..')
from lib.bottle import *
from lib.bottle import request


now = datetime.now()


def TimeGap(date_bef): #get the gap of two date
    date_now = datetime.now()
    if date_now > date_bef:
        gap = date_now - date_bef  #get the gap of two date
        if gap.days < 1 and gap.seconds < 21600: #gap.days get the gap 's days
            if gap.seconds > 3600:
                r = str(int(gap.seconds / 3600)) + '小时前'
                return str(r)

            else:
                r = str(int(gap.seconds / 60)) + '分钟前'
                return str(r)

        else:
            return str(date_bef.strftime('%m-%d %H:%M'))
    else:
        return " "



def get_params(list, request=request):
    params = {}
    for key in list:
        params[key] = request.params.get(key)
    return params


def sql_result(r, key_list, fTime=0):
    #r @tuple 数据库fetchall的结果
    #key_list @list 查询字段的keys
    # format SQL Result 格式化数据库查询的结果，转化成包含多个字典的列表格式，即((1,2),(3,4))->[{"key1":1,"key2":2},{"key1":3,"key2":4}]
    #fTime 是否格式化时间，如果是，时间用TimeGap函数格式化，返回如10分钟前的时间格式
    #返回 @dict 查询结果
    mlist = []
    l = len(key_list)
    if r:
        for item in r:
            tmp = {}
            for i in range(l):
                try:
                    tmp[key_list[i]] = TimeGap(item[i]) if fTime and type(item[i]) == type(now) else item[i]
                except:
                    return str(i)+str(item[i])
            mlist.append(tmp)
    return mlist


def get_sql_index():
    cur_page=request.params.get('cur_page')
    if cur_page:
        try:
            index=(int(cur_page)-1)*20
            return index
        except:
            return None
    else:
        return None