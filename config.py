from webbrowser import Mozilla

url="https://movie.douban.com/top250"
#伪装成浏览器需要加上headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.3',
    'Referer': 'https://www.douban.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cookie':'ll="118088"; bid=PY7VeWpERK0; _pk_id.100001.4cf6=9f94b54e7b8f14e2.1785207963.; _vwo_uuid_v2=DDC7D1F55D21EA3772576FA16A80BCA95|98e17dfbdc511801b3512c59a14c03ac; __utmc=30149280; __utmc=223695111; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1785408983%2C%22https%3A%2F%2Fsec.douban.com%2F%22%5D; _pk_ses.100001.4cf6=1; __utma=30149280.1220024888.1782012587.1785396769.1785408985.6; __utmz=30149280.1785408985.6.4.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/subject/1292052/; __utmt=1; __utmb=30149280.1.10.1785408985; dbcl2="267567614:omigv6Tvc+w"; ck=6Got; __utma=223695111.788775673.1785207962.1785396769.1785409073.5; __utmb=223695111.0.10.1785409073; __utmz=223695111.1785409073.5.4.utmcsr=open.weixin.qq.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0'
}
# 并发数
CONCURRENCY = 5
# 请求超时（秒）
REQUEST_TIMEOUT = 30
# 最大重试次数
MAX_RETRIES = 3
# 数据库配置1
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "movie_db",
    "charset": "utf8mb4"
}
#信号量  asyncio 来控制并发放的
CONCURRENCY = 3#asyncio的Semaphore 信号量 控制并发度