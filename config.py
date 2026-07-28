from webbrowser import Mozilla

url="https://movie.douban.com/top250"
#伪装成浏览器需要加上headers
HEADERS={
    'User-Agent':'Mozilla/5.0(Windows NT 10.0;win64;x64) ApplewedKit/537.36(KHTML,Like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    "database": "douban_db",
    "charset": "utf8mb4"
}