import asyncio
import aiohttp
from bs4 import BeautifulSoup
from db.connection import db_config
from db.movir_repostory import save_movies,get_pending_movies
from crawler.spider import crawl_all_pages, fetch, parse_list_page
from crawler.spider import crawl_pending_movies
#print("数据库配置：", db_config)


async def main():
    async with aiohttp.ClientSession() as session:
        #这是全量查询
        '''
        all_movies = await crawl_all_pages(session)
        save_movies(all_movies)
        '''
        #断点续爬
        await crawl_pending_movies(session)

        #显示所有电影
        '''
        if all_movies:
            print(f"\n共解析到 {len(all_movies)} 部电影")
            for m in all_movies:
                director = m['director'][:30] if m['director'] else '未知'
                print(f"{m['rank']}. {m['mv_title']} | {m['score']}分 | "
                      f"{director} |{m['poster_url']}")
        else:
            print("获取页面失败")
            '''

if __name__ == "__main__":
    asyncio.run(main())