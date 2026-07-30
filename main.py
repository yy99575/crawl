import asyncio
import aiohttp
from bs4 import BeautifulSoup
from db.connection import db_config
from db.movir_repository import save_moviesPython
# from db.movir_repository import save_moviesPython 默认只找同一级目录。
print("数据库配置：", db_config)
print("✅ 所有导入成功，环境准备就绪！")
