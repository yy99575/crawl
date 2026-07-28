import pymysql
from urllib3 import connection

import config

import config
DB=config.DB_CONFIG
#数据库连接
db_config={
    'host': DB['host'],
    'user':DB['user'],
    'password':  DB['password'],
    'database': DB['database'],
    'charset': DB['charset'],
    #'cursorclass': pymysql.cursors.DictCursor  # 使用字典游标
}
#连接数据库
try:
    connection=pymysql.connect(**db_config)
    print("connect success")
except Exception as e:
    print(f"连接数据库失败:{e}")
