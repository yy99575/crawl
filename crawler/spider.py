import aiohttp
import asyncio
from bs4 import BeautifulSoup
import config
import re

url = config.url
headers = config.HEADERS


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            html = await response.text()
            return html
        else:
            print(f"请求失败，状态码：{response.status}")
            return None


def parse_list_page(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('.grid_view .item')
    #print(f"调试：找到 {len(items)} 个条目")
    movies = []

    for item in items:
        # 1. 排名
        rank_elem = item.select_one('.pic em')
        rank = rank_elem.text.strip() if rank_elem else None

        # 2. 片名：只取第一个 .title（中文名）
        # 3. 详情页 URL
        title_elem = item.select_one('.title')  # 选 <span class="title">，不是 <a>
        title = title_elem.text.strip() if title_elem else None
        detail_url = title_elem.parent.get('href') if title_elem and title_elem.parent else None

        # 4. 评分
        score_elem = item.select_one('.rating_num')
        score = score_elem.text.strip() if score_elem else None

        # 5. 评价人数
        spans = item.select('.bd span')
        votes_elem = None
        for span in spans:
            if '人评价' in span.text:
                votes_elem = span
                break
        if votes_elem:
            votes_text = votes_elem.text.strip()
            votes = re.search(r'\d+', votes_text).group() if re.search(r'\d+', votes_text) else None
        else:
            votes = None


        # 6. 导演/主演（第一段）
        director_elem = item.select_one('.bd p')
        if director_elem:
            full_text = director_elem.text.strip()
            lines = full_text.split('\n')
            director = lines[0].strip()

            # 年份和类型从第二行取
            if len(lines) > 1:
                parts = lines[1].split('/')
                release_year = parts[0].strip()
                mv_type = parts[2].strip() if len(parts) > 2 else None
            else:
                release_year = None
                mv_type = None
        else:
            director = None
            release_year = None
            mv_type = None

        #简介
        #introduction
        #海报链接
        poster_url_elem = item.select_one('.pic img')
        poster_url = poster_url_elem.get('src') if poster_url_elem else None

        movie = {
            'rank': rank,
            'mv_title': title,
            'score': score,
            'score_num': votes,
            'detail_url': detail_url,
            'director': director,
            'release_year':release_year,
            'type': mv_type,
            'poster_url': poster_url,

        }
        movies.append(movie)

    return movies  # ✅ 放在循环外面


#翻页
async def crawl_all_pages(session):
    all_movies = []
    for page in range(0, 10):
        start = page * 25
        ping=f"{url}?start={start}"
        html = await fetch(session, ping, headers)
       # print(f"第 {page + 1} 页 HTML 长度: {len(html) if html else 'None'}")
        movies = parse_list_page(html)
        if movies:
            all_movies.extend(movies)
           #print(f"当前页第一条数据: {movies[0] if movies else '空'}")
            #print(f"当前已爬取 {len(all_movies)} 部电影")
        else:
            print("页面为空")
    return all_movies


async def main():
    async with aiohttp.ClientSession() as session:
        all_movies = await crawl_all_pages(session)
        if all_movies:
            print(f"\n✅ 共解析到 {len(all_movies)} 部电影")
            for m in all_movies:
                director = m['director'][:30] if m['director'] else '未知'
                print(f"{m['rank']}. {m['mv_title']} | {m['score']}分 | "
                      f"{director} |{m['poster_url']}")
        else:
            print("获取页面失败")


if __name__ == "__main__":
    asyncio.run(main())