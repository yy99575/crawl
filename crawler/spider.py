from wsgiref import headers

import config
import aiohttp
import asyncio
from bs4 import BeautifulSoup
url=config.url
headers=config.HEADERS
#定义异步函数来获取网页内容fetch() 用 aiohttp 请求一个 URL，拿到 HTML
async def fetch(session,url,headers):
    async with session.get(url) as response:
        # 检查响应状态
        if response.status == 200:
            html = await response.text()
            return html
        else:
            print(f"请求失败，状态码：{response.status}")
            return None
#定义主函数来运行异步内容
async def main():
    async with aiohttp.ClientSession() as session:
        #url=config.url
        #headers=config.HEADERS
        html=await fetch(session,url,headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
       # print(html)
        if html:
            # 调用解析函数
            movies =parse_list_page(html)
            print(f"\n共解析到 {len(movies)} 部电影")
            for m in movies[:3]:
                print(f"{m['rank']}. {m['mv_title']} : {m['score']}分 {m['score_num']} {m['director']}")
        else:
            print("获取页面失败")
#解析页面
def parse_list_page(html):
    soup = BeautifulSoup(html, 'lxml')
    #获取电影列表的电影名称
    """解析列表页，提取每部电影的字段"""
    items = soup.select('.grid_view .item')   # 直接跳过 li
    movies = []
    for item in items:
            # 1. 排名：.pic em
        rank_elem = item.select_one('.pic em')
        rank = rank_elem.text.strip() if rank_elem else None

            # 2. 片名：.title  的文本
        title_elem = item.select_one('.info title')
        title = title_elem.text.strip() if title_elem else None

            # 3. 详情页URL：.title a 的 href
        detail_url = title_elem.get('href') if title_elem else None

            # 4. 评分：.rating_num
        score_elem = item.select_one('.bd rating_num')
        score = score_elem.text.strip() if score_elem else None

            # 5. 评价人数：.star span:last-child
        votes_elem = item.select_one('.bd span:last-child')
        votes = votes_elem.text.strip() if votes_elem else None
            #导演
        director_elem = item.select_one('.bd p')
        director=director_elem.text.strip() if director_elem else None

            # 把所有字段存成一个字典
        movie = {
            'rank': rank,
            'mv_title': title,
            'score': score,
            'score_num': votes,
            'detail_url': detail_url,
            'director': director,
            }
        movies.append(movie)
        #print(movie)
        return movies

#运行主函数
if __name__ == "__main__":
    asyncio.run(main())
