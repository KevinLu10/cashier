# encoding=utf-8

def get_i_sql(table, dict):
    '''
    生成insert的sql语句
    @table，插入记录的表名
    @dict,插入的数据，字典
    '''

    keys, values = zip(*dict.items())

    values = ["'%s'" % x for x in values]
    sql = 'insert into %s(%s) values(%s) ' % (table, ','.join(keys), ','.join(values))

    return sql


def get_s_sql(table, keys, conditions, isdistinct=0):
    '''
        生成select的sql语句
    @table，查询记录的表名
    @key，需要查询的字段
    @conditions,插入的数据，字典
    @isdistinct,查询的数据是否不重复
    '''
    if isdistinct:
        sql = 'select distinct %s ' % ",".join(keys)
    else:
        sql = 'select  %s ' % ",".join(keys)
    sql += ' from %s ' % table
    if conditions:
        sql += ' where %s ' % Dict2StrAnd(conditions)
    return sql


def get_u_sql(table, value, conditions):
    '''
        生成update的sql语句
    @table，查询记录的表名
    @value，dict,需要更新的字段
    @conditions,插入的数据，字典
    '''
    sql = 'update %s set ' % table
    sql += Dict2Str(value)
    if conditions:
        sql += ' where %s ' % Dict2StrAnd(conditions)
    return sql


def get_d_sql(table, conditions):
    '''
        生成detele的sql语句
    @table，查询记录的表名

    @conditions,插入的数据，字典
    '''
    sql = 'delete from  %s  ' % table
    if conditions:
        sql += ' where %s ' % Dict2StrAnd(conditions)
    return sql


def Dict2Str(dictin):
    '''
    将字典变成，key='value',key='value' 的形式
    '''
    tmplist = []
    for k, v in dictin.items():
        tmp = str(k) + '=' + "'" + str(v) + "'"
        tmplist.append(' ' + tmp + ' ')
    return ','.join(tmplist)


def Dict2StrAnd(dictin):
    '''
    将字典变成，key='value' and key='value'的形式
    '''
    tmplist = []
    for k, v in dictin.items():
        tmp = str(k) + '=' + "'" + str(v) + "'"
        tmplist.append(' ' + tmp + ' ')
    return ' and '.join(tmplist)