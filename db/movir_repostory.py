
import pymysql
from pymysql import MySQLError
from db.connection import db_config

#连接数据库

def save_movies(all_movies):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()  # 只需要用一个游标
    print(f"收到{len(all_movies)},准备导入到数据库中")
    for m in all_movies:
        doubao_id=m['detail_url'].split('/')[-2]
        try :
            sql = (
                "INSERT INTO db_movies (doubao_id, mv_title, rank_mv, score, score_num, director, release_year, type, poster_url, detail_url,introduction,crawl_status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s) "
                "ON DUPLICATE KEY UPDATE "
                "mv_title = VALUES(mv_title), "
                "rank_mv = VALUES(rank_mv), "
                "score = VALUES(score), "
                "score_num = VALUES(score_num), "
                "director = VALUES(director), "
                "release_year = VALUES(release_year), "
                "type = VALUES(type), "
                "poster_url = VALUES(poster_url), "
                "detail_url = VALUES(detail_url),"
                "introduction=VALUES(introduction),"
                "crawl_status = VALUES(crawl_status) "
            )
            values=(
                doubao_id,
                m['mv_title'],
                m['rank'],
                m['score'],
                m['score_num'],
                m['director'],
                m['release_year'],
                m['type'],
                m['poster_url'],
                m['detail_url'],
                m['introduction'],
                'pending'
            )
            cursor.execute(sql,values)#sql语句 元组 位置要是一样的
        except MySQLError as e:#数据库异常捕捉错误
            sql=("UPDATE db_movies SET crawl_status = 'failed', last_error = %s WHERE doubao_id = %s")
            cursor.execute(sql, (e,doubao_id))

            print(f"插入数据失败{e}")
    #for 循环执行完 → rollback() → commit() 这个时候就是空事务
    #如果跳过那段有问题的数据 就是不需要rollback
    #如果全成功才能提交 就需要再失败的时候rollback
    conn.commit()  # 所有数据插入好了再提交
    try:
        sql=("UPDATE db_movies SET crawl_status = 'success' WHERE crawl_status = 'pending'")
        cursor.execute(sql)
        print(f"更新了 {cursor.rowcount} 行")  # 加这行
        conn.commit()  # 所有数据插入好了再提交
    except MySQLError as e:
        print(f"更新crawl状态失败：{e}")
    cursor.close()#关闭游标
    conn.close()#关闭数据库
#断点续爬
def get_pending_movies():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    sql = "SELECT doubao_id FROM db_movies WHERE crawl_status IN ('pending', 'failed')"
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results
#pending 从来没爬过 failed 爬过但是失败 success爬过并且成功了

def update_movie_full(movie_data):
    """全量更新电影数据"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 在 SQL 外面构造 detail_url
    detail_url = f"https://movie.douban.com/subject/{movie_data['doubao_id']}/"

    sql = """
          UPDATE db_movies \
          SET mv_title     = %s, \
              score        = %s, \
              score_num    = %s, \
              director     = %s, \
              release_year = %s, \
              type         = %s, \
              introduction = %s, \
              poster_url   = %s, \
              detail_url   = %s, \
              crawl_status = 'success', \
              last_error   = NULL
          WHERE doubao_id = %s \
          """
    cursor.execute(sql, (
        movie_data.get('mv_title'),
        movie_data.get('score'),
        movie_data.get('score_num'),
        movie_data.get('director'),
        movie_data.get('release_year'),
        movie_data.get('type'),
        movie_data.get('introduction'),
        movie_data.get('poster_url'),
        detail_url,
        movie_data['doubao_id']
    ))
    conn.commit()
    conn.close()

def update_movie_status(doubao_id, status, error_msg=None):
    """更新电影状态"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    if error_msg:
        sql = "UPDATE db_movies SET crawl_status = %s, last_error = %s WHERE doubao_id = %s"
        cursor.execute(sql, (status, error_msg, doubao_id))
    else:
        sql = "UPDATE db_movies SET crawl_status = %s WHERE doubao_id = %s"
        cursor.execute(sql, (status, doubao_id))
    conn.commit()
    conn.close()


