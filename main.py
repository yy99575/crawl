import asyncio
import aiohttp
from crawler.spider import crawl_all_pages, crawl_pending_movies
from db.movir_repostory import save_movies
from db.connection import db_config
import pymysql


def print_stats():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM db_movies")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM db_movies WHERE crawl_status = 'success'")
    success = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM db_movies WHERE crawl_status = 'pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM db_movies WHERE crawl_status = 'failed'")
    failed = cursor.fetchone()[0]
    conn.close()

    print("\n" + "=" * 40)
    print("------------爬取统计------------")
    print("=" * 40)
    print(f"  总电影数:   {total}")
    print(f"  已成功:    {success}")
    print(f"  待爬:     {pending}")
    print(f"  失败:     {failed}")
    print("=" * 40)


async def main():
    async with aiohttp.ClientSession() as session:
        choice = input("请输入模式：1--全量爬取  0--断点续爬：")

        if choice == "1":
            print("开始全量爬取...")
            all_movies = await crawl_all_pages(session)
            save_movies(all_movies)
            print_stats()
            if all_movies:
                print(f"\n共解析到 {len(all_movies)} 部电影")
                # 只打印前5条预览
                for m in all_movies[:5]:
                    director = m['director'][:30] if m['director'] else '未知'
                    print(f"{m['rank']}. {m['mv_title']} | {m['score']}分 | {director}")
            else:
                print("获取页面失败")

        elif choice == "0":
            print("开始断点续爬...")
            updated = await crawl_pending_movies(session)
            print_stats()
            if updated:
                print(f"本次更新了 {len(updated)} 部电影")
        else:
            print("输入无效，请输入 1 或 0")


if __name__ == "__main__":
    asyncio.run(main())