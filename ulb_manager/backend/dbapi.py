# 从django的http模块中导入Http回应模块，响应前端发来的api请求

from django.http import HttpResponse
from django.http import FileResponse
from django.http import Http404
import json
import pymysql  # 操作数据库，响应前端查询数据库的请求
import xlwt

# 用于登录数据库的全局变量
db = ''
table = ''
user = ''
passwd = ''

# login方法，为用户提供登录自己数据库的接口，而不是我预设的数据库用户名和密码
def login(req):
    global user
    global passwd
    user = req.GET.get('username')
    passwd = req.GET.get('password')
    conn = pymysql.Connect(
        host='localhost',
        port=3306,
        user=user,
        passwd=passwd,
        charset='utf8',
        db='mysql'
    )
    if(conn):
        return HttpResponse('success')
    else:
        return Http404()


def _connect(db):  # 为所有函数一个connect连接对象
    global user
    global passwd
    conn = pymysql.Connect(
        host='localhost',
        port=3306,
        user=user,
        passwd=passwd,
        db=db,
        charset='utf8'
    )
    return conn


def _conn(db):  # 为所有函数提供一个游标对象
    global user
    global passwd
    conn = pymysql.Connect(
        host='localhost',
        port=3306,
        user=user,
        passwd=passwd,
        db=db,
        charset='utf8'
    )
    return conn.cursor()



# 创建一个响应前端查询数据库的请求的方法
# 以下相关参数可以换成自己的
# 数据库名：sims 用户名：root 本地主机：localhost 端口：3306 密码：asd58108181
def dbapi(req):

    if(req.GET.get('db') == None):
        return HttpResponse('<i style="color: red;font-size: 30px">错误，未指定数据库名!</i>')
    elif(req.GET.get('table') == None):
        return HttpResponse('<i style="color: red;font-size: 30px">错误，未指定数据表名! 当前查询的数据库为：'+req.GET.get('db')+'</i>')

    # 声明使用全局变量
    global db
    global table

    db = str(req.GET.get('db'))
    table = str(req.GET.get('table'))

    res = {
        'columns': [],
        'tips': [],
        'data': [],
        'count': 0,
        'dbs': []
    }
    cursor = _conn(db)

    # 查询列名
    # sql = 'SHOW COLUMNS from %s'
    # cursor.execute(sql % table)
    # for row in cursor.fetchall():
    #     res['columns'].append(row[0])

    # 查询列名和注释
    sql = "SELECT COLUMN_NAME,column_comment FROM INFORMATION_SCHEMA.Columns WHERE table_name='%s' AND table_schema='%s'"
    cursor.execute(sql % (table,db))
    for row in cursor.fetchall():
        res['columns'].append(row[0])
        res['tips'].append(row[1])

    sql = "SELECT * FROM %s"# 从指定表中查询所有数据
    cursor.execute(sql % table)
    res['count'] = cursor.rowcount
    print(res['tips'])
    print(res['columns'])
    tmp = []
    tmp2 = []
    for i in cursor.description:
        tmp.append(i[0])
    print(tmp)
    # 因为从数据库里查询到的列名和注释都是乱序的
    for i in range(0,len(tmp)):
        for j in range(0,len(tmp)):
            if (tmp[i] == res['columns'][j]):
                tmp2.append(res['tips'][j])
    res['tips'] = tmp2
    res['columns'] = tmp
    for row in cursor.fetchall():
        obj = {}
        for i in range(0,len(row)):
            obj[res['columns'][i]] = str(row[i])
        res['data'].append(obj)

    # 如果前端是第一次访问则dbs=='0'就查询数据库名和表名,否则不查 节省资源
    if(req.GET.get('dbs') == '0'):
        print('查询数据库名')
        # 查询所有数据库的执行结果是一个个元组,所以要用dbName[0]只拿第一个数据库名
        sql = 'show DATABASEs'
        cursor.execute(sql)
        for dbName in cursor.fetchall():
            tmp1 = {}
            tmp2 = []
            if (dbName[0] == 'information_schema' or dbName[0] == 'sys'  or dbName[0] == 'performance_schema'):
                continue

            sql = "SELECT table_name from information_schema.tables WHERE table_schema='%s'"
            cursor.execute(sql % (dbName[0]))
            for tableName in cursor.fetchall():
                # 同理,查询数据库的数据表也是一个元组,也要用row[0]取第一个值
                tmp2.append(tableName[0])
            tmp1['dbName'] = dbName[0]
            tmp1['tables'] = tmp2
            res['dbs'].append(tmp1)

    # 同理,查询数据库的数据表也是一个元组,也要用row[0]取第一个值
    # sql = "SELECT table_name from information_schema.tables WHERE table_schema='sims' "
    # cursor.execute(sql)
    # for row in cursor.fetchall():
    #     print(row)
    # 切记返回一个Http回应
    return HttpResponse(json.dumps(res),content_type='application/json')

# 添加测试接口，接收前端的请求，并返回一个json数据
# 按请求的条件查询
def select(request):
    global db
    global table
    print(db,table)

    # 如果是GET请求
    if(request.method == 'GET'):
        print(request.GET) # .GET.get()表示从GET请求中 获得 特定键值的请求的内容，比如api/testapi?a=Hello 则get('a')的值为Hello

        # response为响应发送给前端的数据
        if(request != None):
            res = {
                'col': [],
                'data': [],
                'count': 0
            }
            cursor = _conn(db)

            # 查询列名
            sql = 'SHOW COLUMNS from %s'
            cursor.execute(sql % table)
            for row in cursor.fetchall():
                res['col'].append(row[0])

            sql = "SELECT * FROM %s WHERE "
            query = request.GET
            for i in query:
                if(query[i]) != '':
                    q = str(query[i])
                    sql = sql + f"{i}='{q}' AND "

            sql = sql[:-4]
            print('欸嘿嘿')
            cursor.execute(sql % table)
            for row in cursor.fetchall():
                obj = {}
                for i in range(0, len(row)):
                    obj[res['col'][i]] = str(row[i])  # 有时数据库的字段类型并不是JSON允许的类型所以一定要用str()函数将其转为字符串
                res['data'].append(obj)
            res['count'] = cursor.rowcount
            return HttpResponse(json.dumps(res), content_type='application/json')
        else:
            response = {
                'errorcode': 100,
                'type': 'GET',
                'msg': 'error'
            }
            # return，使用HttpResponse响应方法发送Http回应，第一个参数为响应的内容，第二个参数为Http响应的类型是json类型
            return HttpResponse(json.dumps(response), content_type='application/json')

# 按条件模糊查询
def mselect(request):
    global db
    global table
    # 如果是GET请求
    if (request.method == 'GET'):
        print(request.GET)  # .GET.get()表示从GET请求中 获得 特定键值的请求的内容，比如api/testapi?a=Hello 则get('a')的值为Hello

        # response为响应发送给前端的数据
        if (request != None):
            res = {
                'col': [],
                'data': [],
                'count': 0
            }
            cursor = _conn(db)

            # 查询列名
            sql = 'SHOW COLUMNS from %s'
            cursor.execute(sql % table)
            for row in cursor.fetchall():
                res['col'].append(row[0])

            sql = "SELECT * FROM %s WHERE "
            query = request.GET
            for i in query:
                if (query[i]) != '':
                    q = str(query[i])
                    sql = sql + f"{i}='{q}' OR "

            sql = sql[:-3]
            print(sql)

            cursor.execute(sql % table)
            for row in cursor.fetchall():
                obj = {}
                for i in range(0, len(row)):
                    obj[res['col'][i]] = str(row[i])
                res['data'].append(obj)
            res['count'] = cursor.rowcount
            return HttpResponse(json.dumps(res), content_type='application/json')
        else:
            response = {
                'errorcode': 100,
                'type': 'GET',
                'msg': 'error'
            }
            # return，使用HttpResponse响应方法发送Http回应，第一个参数为响应的内容，第二个参数为Http响应的类型是json类型
            return HttpResponse(json.dumps(response), content_type='application/json')

        #简单一点，只使用get请求。
# 按请求的id删除
def delete(request):
    global db
    global table
    conn = _connect(db)
    cursor = conn.cursor()
    # 如果是GET请求
    if(request.GET.get('method') != 'multiple'):

        id = request.GET.get('id')
        print(id)
        sql = "delete from %s where id = %s"

        cursor.execute(sql % (table,id))
        # 删除，更新，插入操作还需要用connect链接来提交事务
        conn.commit()
        print(cursor.rowcount)

        if(cursor.rowcount != 0):
            return HttpResponse('success')
        else:
            return HttpResponse('not found')
    else:
        sql = "delete from %s where "
        # 需要使用json库将前端发来的请求(字符串类型)转为python数据类型
        id = json.loads(request.GET.get('id'))
        for i in id:
            sql = sql + "id='" + str(id[i]) + "' OR "
        sql = sql[:-3]
        print(sql)
        cursor.execute(sql % (table))
        conn.commit()

        if(cursor.rowcount != None):
            res = {
                'msg': 'success',
                'count': cursor.rowcount
            }
            return HttpResponse(json.dumps(res),content_type='application/json')
        else:
            res = {
                'msg': 'error'
            }
            return HttpResponse(json.dumps(res),content_type='application/json')


def insert(req):
    global db
    global table
    conn = _connect(db)
    cursor = conn.cursor()

    data = req.GET
    # print(data)
    cols = "("
    value = "("
    for i in data:
        cols = cols + '`' + i + '`,'
        value = value + "'"+ str(data[i]) + "',"
    cols = cols[:-1] + ')'
    value = value[:-1] + ')'

    print(cols)
    print(value)

    sql = "INSERT INTO %s %s VALUES %s"
    cursor.execute(sql % (table,cols,value))
    conn.commit()
    print(cursor.rowcount)
    if(cursor.rowcount != 0):
        res = {'msg': 'success','count': cursor.rowcount}
        return HttpResponse(json.dumps(res),content_type='application/json')
    else:
        return HttpResponse('error')

def edit(req):
    global db
    global table

    conn = _connect(db)
    cursor = conn.cursor()

    data = req.GET
    print(data)
    id = data.get('id')
    print(id)
    cols = ""
    for i in data:
        cols = cols + '`' + i + "`='" + str(data[i]) + "',"
    cols = cols[:-1]

    print(cols)
    print(table)

    sql = "UPDATE %s SET %s WHERE id = %s"

    cursor.execute(sql % (table, cols, id))
    conn.commit()
    print(cursor.rowcount)
    print(type(cursor.rowcount))
    if (cursor.rowcount != None):
        res = {'msg': 'success', 'count': cursor.rowcount}
        return HttpResponse(json.dumps(res), content_type='application/json')
    else:
        return HttpResponse('error')

# 所有程序的入口都是根目录下的mangee.py，所以保存文件的命令也是在根目录下执行的，所以文件会被保存在根目录下而不是当前目录
def export(req):
    file = xlwt.Workbook() #新建一个Excel文件
    table = file.add_sheet('test')
    table.write(0,0,'test')
    # 所以选择文件保存路径的时候要以根目录为起点
    file.save('./backend/file/test.xls')
    fp = open('./backend/file/test.xls','rb')
    res = FileResponse(fp,content_type='application/excel')
    res['Content-Disposition'] = 'attachment;filename="test.xls"'
    return res




