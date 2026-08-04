import aiohttp
import asyncio
from bs4 import BeautifulSoup
import config
import re
from db.movir_repostory import save_movies,get_pending_movies,update_movie_full,update_movie_status

url = config.url
headers = config.HEADERS

#异步请求
async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            html = await response.text()
            return html
        else:
            print(f"请求失败，状态码：{response.status}")
            return None

#解析html 大大多数字段都是在这里
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
                year_str = parts[0].strip()
                match = re.search(r'\d{4}', year_str)
                release_year = int(match.group()) if match else None
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
            'introduction': None
        }
        movies.append(movie)

    return movies  # ✅ 放在循环外面


#翻页
async def crawl_all_pages(session):
    semaphore = asyncio.Semaphore(config.CONCURRENCY)
    all_movies = []
    for page in range(0, 10):
        start = page * 25
        ping=f"{url}?start={start}"
        async with semaphore:
            html = await fetch(session, ping, headers)
       # print(f"第 {page + 1} 页 HTML 长度: {len(html) if html else 'None'}")
        if html:
            movies = parse_list_page(html)
        else:
            print(f"{page+1}页面请求失败 跳过")
            continue
        if movies:
            all_movies.extend(movies)
           # brief_url=movies[0]['detail_url']
            for movie in movies:
                async  with semaphore:
                    detail_html = await fetch(session, movie['detail_url'], headers)
                await asyncio.sleep(2)#每请求完一个详情页都需要缓缓 防止被豆瓣封 0.3太短了 引起了429 素以需要增加延迟
                if detail_html:
                    intro = parse_intro_page(detail_html)
                    movie['introduction'] = intro
                else:
                    movie['introduction'] = None
                    '''
                if intro:
                    print(f"{movie['mv_title']}: {intro[:30]}...")
                else:
                    print(f" {movie['mv_title']}: 简介为空")
                    '''
           #print(f"当前页第一条数据: {movies[0] if movies else '空'}")
            #print(f"当前已爬取 {len(all_movies)} 部电影")
        else:
            print("页面为空")
    return all_movies

#解析电影简介 需要跳转
def parse_intro_page(html):
    soup = BeautifulSoup(html, 'lxml')
    intro_elem = soup.select_one('meta[property="og:description"]')
    intro_text = intro_elem.get('content') if intro_elem else None
    return intro_text

 #断点续爬：重新爬取所有 pending 或 failed 的电影
async def crawl_pending_movies(session):
    pending = get_pending_movies()  # 从数据库获取需要爬的列表
    if not pending:
        print("所有电影已爬完")
        return []  # 返回空列表表示没有需要更新的
    print(f" 需要续爬 {len(pending)} 部电影")
    updated = []
    for row in pending:
        doubao_id = row[0]  # 取出 doubao_id
        detail_url = f"https://movie.douban.com/subject/{doubao_id}/"
        # 请求详情页
        detail_html = await fetch(session, detail_url, headers)
        await asyncio.sleep(2)  # 控制频率
        if detail_html:
            # 解析详情页所有字段
            movie_data = parse_detail_page(detail_html, doubao_id)
            if movie_data:
                # 更新数据库（全量更新 + 状态改为 success）
                update_movie_full(movie_data)
                updated.append(doubao_id)
                print(f"   {doubao_id} 已更新")
            else:
                # 解析失败，保持 pending 或改为 failed
                update_movie_status(doubao_id, 'failed', '解析失败')
                print(f"   {doubao_id} 解析失败")
        else:
            # 请求失败，保持 pending 或改为 failed
            update_movie_status(doubao_id, 'failed', '请求失败')
            print(f"  {doubao_id} 请求失败")
    return updated

#解析详情页所有字段
def parse_detail_page(html, doubao_id):
    soup = BeautifulSoup(html, 'lxml')
    # 从 meta 标签取
    title_elem = soup.select_one('meta[property="og:title"]')
    title = title_elem.get('content') if title_elem else None

    score_elem = soup.select_one('.rating_num')
    score = score_elem.text.strip() if score_elem else None

    intro_elem = soup.select_one('meta[property="og:description"]')
    intro = intro_elem.get('content') if intro_elem else None

    poster_elem = soup.select_one('meta[property="og:image"]')
    poster = poster_elem.get('content') if poster_elem else None
    # 这些字段从列表页已经有了，但续爬时也要更新
    # 如果详情页取不到，用数据库里的旧值
    # 最好从数据库查出旧值，这里只更新能取到的
    return {
        'doubao_id': doubao_id,
        'mv_title': title,
        'score': score,
        'introduction': intro,
        'poster_url': poster
    }