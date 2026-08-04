from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from db.connection import db_config
import pymysql


app = FastAPI()#创建一个fastapi实例
#定义根路径的get路由

#允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/movies")
#定义了一个接口，它接收两个可选参数。如果用户不传，就按评分降序排列 分页参数 页数和每页的大小
async def get_movies(sort_by:str="score",order:str="desc",page:int=1,page_size:int=10):
    conn = pymysql.connect(**db_config)  # 连接数据库
    cursor = conn.cursor()#游标
    # 可以查询的白名单
    order_field = {
        "rank":"rank_mv",
        "score":"score",
        "score_num":"score_num",
        "release_year":"release_year",
    }
    # 校验 sort_by 是否在白名单里
    if sort_by not in order_field:
        return {"error":f"不支持的排序字段：{sort_by}"}
    #校验order是asc还是desc
    if order not in ["asc","desc"]:
        return { "error":f"order只能是asc或者是desc"}
    field=order_field[sort_by]
    #先排序后分页
    limit_page=page_size
    offset_page=(page-1)*page_size
    sql_total=f"SELECT COUNT(*) FROM db_movies"
    cursor.execute(sql_total)
    total=cursor.fetchone()[0]
    sql=f"SELECT * FROM db_movies order by {field} {order} limit {limit_page} offset {offset_page}"
    cursor.execute(sql)
    result=cursor.fetchall()
    conn.close()
    #转换成字典列表 （方便前端使用）
    movies=[]
    for row in result:
        movies.append({
            "id":row[0],
            "doubao_id":row[1],
            "title":row[2],
            "rank":row[3],
             "score":row[4],
            "score_num":row[5],
            "director":row[6],
            "release_year":row[7],
            "type":row[8],
            "introduction":row[9],
            "poster_url":row[10],
        })
    return {
        "items":movies,
        "total":total,
        "page":page,
        "page_size":page_size,
    }



