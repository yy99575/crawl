
import pymysql
from pymysql import MySQLError
from db.connection import db_config

#连接数据库
conn=pymysql.connect(**db_config)
cursor=conn.cursor()#只需要用一个游标
def save_movies(all_movies):
    for m in all_movies:
        douban_id=m['detail_url'].split('/')[-2]
        try :
            sql = (
                "INSERT INTO db_movies (douban_id, mv_title, rank_mv, score, score_num, director, release_year, type, poster_url, detail_url) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "mv_title = VALUES(mv_title), "
                "rank_mv = VALUES(rank_mv), "
                "score = VALUES(score), "
                "score_num = VALUES(score_num), "
                "director = VALUES(director), "
                "release_year = VALUES(release_year), "
                "type = VALUES(type), "
                "poster_url = VALUES(poster_url), "
                "detail_url = VALUES(detail_url)"
            )
            values=(
                douban_id,
                m['mv_title'],
                m['rank'],
                m['score'],
                m['score_num'],
                m['director'],
                m['release_year'],
                m['type'],
                m['poster_url'],
                m['detail_url']
            )
            cursor.execute(sql,values)#sql语句 元组 位置要是一样的
        except MySQLError as e:#数据库异常捕捉错误
            print(f"插入数据失败{e}")
    #for 循环执行完 → rollback() → commit() 这个时候就是空事务
    #如果跳过那段有问题的数据 就是不需要rollback
    #如果全成功才能提交 就需要再失败的时候rollback
    conn.commit()#所有数据插入好了再提交
    cursor.close()#关闭游标
    conn.close()#关闭数据库

