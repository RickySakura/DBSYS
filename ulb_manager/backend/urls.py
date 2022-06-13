from django.urls import  path
from . import dbapi

urlpatterns = [
    # 添加另一个让后端查询数据库的api接口
    path('login', dbapi.login, name='login'),  # 数据库登录接口
    path('dbapi',dbapi.dbapi,name='dbapi'),  # 数据库请求总接口，负责查询所有字段(包括数据库名、表名、列名、注释以及字段数据)
    path('select', dbapi.select, name='select'), # 查询接口，负责精确地按条件查询数据
    path('mselect', dbapi.mselect, name='mselect'), # 查询接口，负责进行模糊地按条件查询数据
    path('delete', dbapi.delete, name='delete'), # 删除接口，删除数据库字段
    path('insert', dbapi.insert, name='insert'), # 插入接口，负责插入前端提交的数据
    path('edit', dbapi.edit, name='edit'), # 修改接口，根据前端提交的数据更新数据库字段

    path('export', dbapi.export, name='export'), # 原导出接口，负责响应文件下载请求(现已弃用)
]

